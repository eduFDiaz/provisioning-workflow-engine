import { AfterViewInit, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { MilestoneHttpService } from '../milestone-http-service.service';
import { Milestone } from '../Models/Milestone';
import { Observable, forkJoin } from 'rxjs';
import { MilestoneWsService } from '../milestone-ws-service.service';
import { Subscription } from 'rxjs';
import { Workflow } from '../Models/Workflow';

import { ElementRef, QueryList, ViewChildren } from '@angular/core';
import { HttpResponse } from '@angular/common/http';
import { SessionService } from '../session.service';

@Component({
  selector: 'app-milestone-group',
  templateUrl: './milestone-group.component.html', 
  styleUrls: ['./milestone-group.component.scss']
})
export class MilestoneGroupComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChildren('stepTitle') stepTitles: QueryList<ElementRef> | undefined;
  milestones: Map<string, Milestone[]> = new Map<string, Milestone[]>();
  milestonesArray: [string, Milestone[]][] = [];
  workflowsArray: Workflow[] = [];
  workflowFileName = "l3vpn-provisioning/vpn_provisioning.yml";
  repoName = "network-workflows";
  branch = "feature-issues-18";
  messagesSubscription!: Subscription;
  startTowerStatus = "not-started";
  CompleteTowerStatus = "not-started";
  constructor(private http: MilestoneHttpService,
              private ws: MilestoneWsService,
              private cd: ChangeDetectorRef,
              private session: SessionService) { }

  ngAfterViewInit(): void {
    this.stepTitles?.changes.subscribe(() => {
      this.stepTitles?.forEach((titleElement) => {
        const element = titleElement.nativeElement;
        const height = element.getBoundingClientRect().height;
        const width = element.getBoundingClientRect().width;

        element.style.transform = `translate(-${width / 2 + 30}px, -${height+10}px)`;
        element.style.textAlign = 'center';
      });

      // Manually triggering change detection
      this.cd.detectChanges();
    });
  }
  
  ngOnInit(): void {
    this.updateDashboard();
  }

  ngOnDestroy(): void {
    this.ws.close();
    if (this.messagesSubscription) {
      this.messagesSubscription.unsubscribe();
    }
  }

  startWorkflow(): void {
    console.log('Starting workflow');
    let requestID = this.session.getSessionVar('request-id');
    this.http.startWorkflow(this.workflowFileName, requestID, this.repoName, this.branch)
    .subscribe(
      (response: any) => {
        let requestID = response['request-id'] as string;
        console.log(`requestID from response body: ${requestID}`);

        let date = new Date();
        date.setMonth(date.getMonth() + 1);
        this.session.setSessionVar('request-id', requestID, date);
        
        this.subscribeToMessages(requestID);
      },
      error => {
        console.log(error);
      }
    );
  }

  updateDashboard(): void {
    let requestID = this.session.getSessionVar('request-id');
    console.log(`requestID from cookie: ${requestID}`);

    if (requestID) {
      const milestones$: Observable<Record<string, Milestone[]>> = this.http.getMilestones(this.workflowFileName, requestID) as Observable<Record<string, Milestone[]>>;
      const milestonesStatus$: Observable<Milestone[]> = this.http.getMilestonesStatus(this.workflowFileName, requestID) as Observable<Milestone[]>;
  
      forkJoin([milestones$, milestonesStatus$]).subscribe(([milestonesRes, milestonesStatusRes]) => {
        console.log(milestonesRes);
        console.log(milestonesStatusRes);
  
        this.milestones = new Map<string, any>(Object.entries(milestonesRes));
        this.milestonesArray = Array.from(this.milestones.entries());
  
        // find each element of milestonesStatusRes in this.milestones and merge them using the spread operator
        milestonesStatusRes.forEach(milestone => {
          const arrayIndex = this.milestonesArray.findIndex(milestones => milestones[0] === milestone.workflow);
          console.log(arrayIndex);
          if (arrayIndex !== -1) {
            const milestoneIndex = this.milestonesArray[arrayIndex][1].findIndex(milestones => milestones.step === milestone.step);
            console.log(milestoneIndex);
            if (milestoneIndex !== -1) {
              this.milestonesArray[arrayIndex][1][milestoneIndex] = {...this.milestonesArray[arrayIndex][1][milestoneIndex], ...milestone};
              console.log(this.milestonesArray[arrayIndex][1][milestoneIndex]);
            }
          }
        });
        
        this.updateWorkflowArray();
      });
    }
  }

  updateWorkflowArray(): void {
    // This method updates the workflowsArray based on the milestonesArray resoponse received initially or
    // when new milestone notifications are received from the websocket connection
    this.workflowsArray = [];

    this.milestonesArray.forEach(([workflow, milestones]) => {
      let status = "";
      // count all the milestones that are completed
      const completedMilestones = milestones.filter(milestone => milestone.status === "completed").length;
      // count all the milestones that are in-progress
      const inProgressMilestones = milestones.filter(milestone => milestone.status === "in-progress").length;
      // count all the milestones that are not-started
      const notStartedMilestones = milestones.filter(milestone => milestone.status === "not-started").length;
      // count all the milestones that are failed
      const failedMilestones = milestones.filter(milestone => milestone.status === "failed").length;
      // if all the milestones are completed, then the workflow is completed
      if (completedMilestones === milestones.length) {
        status = "completed";
      } else if (inProgressMilestones > 0) {
        // if there are any milestones that are in-progress, then the workflow is in-progress
        status = "in-progress";
      } else if (notStartedMilestones === milestones.length) {
        // if all the milestones are not-started, then the workflow is not-started
        status = "not-started";
      } else if (failedMilestones > 0) {
        // if there are any milestones that are failed, then the workflow is failed
        status = "failed";
      }
      // declare a temporary workflow object
      let tmpWorkflow: Workflow = { 
        workflowName: workflow,
        milestones: milestones,
        status: status
      } as Workflow;

      console.log(tmpWorkflow);

      this.workflowsArray.push(tmpWorkflow);
    });

    this.updateStartAndEndTowerStatus();
  }
  
  updateStartAndEndTowerStatus(): void {
    // This method updates the startTowerStatus and CompleteTowerStatus based on the workflowsArray elements status
    // count all the workflows that are completed
    const completedWorkflows = this.workflowsArray.filter(workflow => workflow.status === "completed").length;
    // count all the workflows that are in-progress
    const inProgressWorkflows = this.workflowsArray.filter(workflow => workflow.status === "in-progress").length;
    // count all the workflows that are not-started
    const notStartedWorkflows = this.workflowsArray.filter(workflow => workflow.status === "not-started").length;
    // count all the workflows that are failed
    const failedWorkflows = this.workflowsArray.filter(workflow => workflow.status === "failed").length;

    if (completedWorkflows === this.workflowsArray.length) {
      // if all the workflows are completed, then the startTowerStatus is completed
      this.startTowerStatus = "completed";
    } else if (inProgressWorkflows > 0) {
      // if there are any workflows that are in-progress, then the startTowerStatus is in-progress
      this.startTowerStatus = "in-progress";
    } else if (notStartedWorkflows === this.workflowsArray.length) {
      // if all the workflows are not-started, then the startTowerStatus is not-started
      this.startTowerStatus = "not-started";
    } else if (failedWorkflows > 0) {
      // if there are any workflows that are failed, then the startTowerStatus is failed
      this.startTowerStatus = "failed";
    }

    if (this.startTowerStatus === "completed") {
      // if all the workflows are completed, then the completeTowerStatus is completed
      this.CompleteTowerStatus = "completed";
    } else {
      this.CompleteTowerStatus = "not-started";
    }
  }

  retryFlow($event: string) {
    console.log("retry flow from parent", $event);
    this.startWorkflow();
  }

  subscribeToMessages(requestID: string): void {
    this.messagesSubscription = this.ws.connect(`ws://localhost:4040/ws/?client_id=${requestID}`).
    subscribe(
      message => {
        console.log('Received: ' + message);
        if (message !== 'ping') {
            // parse the message as a Milestone object
            var tmpMilestone: Milestone = JSON.parse(message);
            console.log(tmpMilestone, typeof(tmpMilestone));
            // find the element in the milestoneArray that contains the milestone received and merge it with the newly received tmpMilestone using spread operator
            const arrayIndex = this.milestonesArray.findIndex(milestone => milestone[0] === tmpMilestone.workflow);
            if (arrayIndex !== -1) {
                const milestoneIndex = this.milestonesArray[arrayIndex][1].findIndex(milestone => milestone.step === tmpMilestone.step);
                if (milestoneIndex !== -1) {
                    console.log('milestone before update', this.milestonesArray[arrayIndex][1][milestoneIndex]);
                    this.milestonesArray[arrayIndex][1][milestoneIndex] = {...this.milestonesArray[arrayIndex][1][milestoneIndex], ...tmpMilestone};
                    console.log('milestone after update', this.milestonesArray[arrayIndex][1][milestoneIndex]);
                }
            }
            this.cd.detectChanges();
            console.log(this.milestonesArray);
            this.updateWorkflowArray();
        }
      },
      error => console.error('Error: ' + error),
      () => {
        this.sendMessage();
        console.log('Completed');
      }
    );
  }
  
  // When you want to send a message
  sendMessage(): void {
    console.log('Sending a message');
    this.ws.send('Hello from Angular!');
  }
}


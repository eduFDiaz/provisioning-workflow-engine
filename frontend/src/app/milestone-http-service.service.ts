import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Milestone } from './Models/Milestone';
import { Observable, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MilestoneHttpService {
  httpClient: HttpClient;
  mockMilestones: Milestone[];

  constructor(private http: HttpClient) { 
    this.httpClient = http;
    this.mockMilestones = [
      {
          "correlationID": "0c32b683-683a-4de4-a7f3-44318a14acbc",
          "workflow": "phy_interface_vrf",
          "status": "completed",
          "step": "Fetch_order_configs",
          "milestoneName": "phy interface vrf activation milestoneName",
          "milestoneStepName": "Fetch the order configs milestoneStepName",
          "startTime": "2023-05-26 UTC 14:41:32",
          "endTime": "2023-05-26 UTC 14:41:32",
          "description": "Fetching order configs for flow steps"
      },
      {
          "correlationID": "0c32b683-683a-4de4-a7f3-44318a14acbc",
          "workflow": "phy_interface_vrf",
          "status": "completed",
          "step": "clean_up_vrf_config",
          "milestoneName": "phy_interface_vrf",
          "milestoneStepName": "clean_up_vrf_config",
          "startTime": "2023-05-26 UTC 14:41:33",
          "endTime": "2023-05-26 UTC 14:41:44",
          "description": "deleting vrf configs from the device"
      },
      {
          "correlationID": "0c32b683-683a-4de4-a7f3-44318a14acbc",
          "workflow": "netconf_vrf_steps",
          "status": "completed",
          "step": "add_vrf_definition",
          "milestoneName": "netconf_vrf_steps",
          "milestoneStepName": "add_vrf_definition",
          "startTime": "2023-05-26 UTC 14:41:45",
          "endTime": "2023-05-26 UTC 14:41:47",
          "description": "adding vrf definition configs to the device"
      },
      {
          "correlationID": "0c32b683-683a-4de4-a7f3-44318a14acbc",
          "workflow": "netconf_vrf_steps",
          "status": "completed",
          "step": "add_prefix_lists",
          "milestoneName": "netconf_vrf_steps",
          "milestoneStepName": "add_prefix_lists",
          "startTime": "2023-05-26 UTC 14:41:48",
          "endTime": "2023-05-26 UTC 14:41:50",
          "description": "adding prefix lists configs to the device"
      },
      {
          "correlationID": "0c32b683-683a-4de4-a7f3-44318a14acbc",
          "workflow": "netconf_vrf_steps",
          "status": "failed",
          "step": "add_route_maps",
          "milestoneName": "netconf_vrf_steps",
          "milestoneStepName": "add_route_maps",
          "startTime": "2023-05-26 UTC 14:41:51",
          "endTime": "2023-05-26 UTC 14:41:52",
          "description": "adding route maps configs to the device"
      }
  ];
  }

  getMilestones(workflowFileName: string, requestID: string) {
    // This is a call to WORKFLOW MS (The PRODUCER APP which has the inventory of all the workflows file definitions)
    var url = `http://localhost:8000/fetch_flow_steps/?workflowFileName=${workflowFileName}&requestID=${requestID}`
    console.log("url: ", url);
    return this.httpClient.get(url);
  }

  getMilestonesStatus(workflowFileName: string, requestID: string) {
    // remove to get the milestones from the mock data instead of the notification MS Cassandra DB
    // return this.getMockMilestones();
    // this is a call to NOTIFICATION MS (The CONSUMER APP which has the casssandra DAO to fetch the milestones status)
    var url = `http://localhost:8000/notification/?&requestID=${requestID}`;
    console.log("url: ", url);
    return this.httpClient.get(url);
  }

  getMockMilestones() {
    // return an observable of type Milestone[]
    return of(this.mockMilestones);
  }

  startWorkflow(workflowFileName: string, requestID: string) {
    //Create the headers for the post request adding requestID to it
    let httpHeaders = new HttpHeaders();

    if (requestID != null && requestID != undefined && requestID != "") {
      console.log(`append requestID to the headers - request_id: ${requestID}`);
      httpHeaders = httpHeaders.append('request_id', requestID);
    } else {
      console.log("requestID is null or undefined or empty");
    }

    let options = {headers: httpHeaders};
    
    return this.httpClient.post(`http://localhost:8000/execute_workflow/?flowFileName=${workflowFileName}`, options);
  }
}

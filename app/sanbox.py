from contextvars import Context, ContextVar, copy_context

# Create context variables
var1 = ContextVar('var1')

# Set values for the context variables
var1.set("Variable 1")

# Copy the current context
ctx: Context = copy_context()

var2 = ContextVar('var2')
var2.set(42)

# Print the list of context items
print(list(ctx.items()))

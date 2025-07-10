from langfuse import Langfuse

langfuse = Langfuse(
    secret_key="sk-lf-78715c5a-3d7f-4efa-8698-4b04717ca658",
    public_key="pk-lf-47e72ad2-6484-4c33-9677-4e9242508895",
    host="https://cloud.langfuse.com",
)

# Verify connection, do not use in production as this is a synchronous call
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

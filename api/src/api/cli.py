import click
import os 
import uvicorn

# create click command
@click.group()
def cli():
    pass

# create command for click cli
@cli.command()
def up():
    #  use uvicorn to run api
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)



if __name__ == "__main__":
    cli()



    



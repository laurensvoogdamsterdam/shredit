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
    os.system("uvicorn api.src.api:app --reload")
    uvicorn.run("src.api:app", host="



if __name__ == "__main__":
    cli()
``` 



    



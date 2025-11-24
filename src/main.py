import os
import shlex
import typer
from typing import List
from src.commands import Operations,input_check
from src.logger import setup_logging, get_logger

setup_logging()
logger = get_logger()

home_dir=os.path.expanduser("~")
os.chdir(home_dir)
app=typer.Typer()

@app.command()
def ls(path: str = typer.Argument("."),
        key: bool = typer.Option(False, "-l")):
    if path == ".":
        path = os.getcwd()
    obj = Operations(path,key)
    for i in obj.ls():
        print(i)

@app.command()
def cd(path: str = typer.Argument("."),key=False):
    if path == ".":
        path = os.getcwd()
    if path == '~':
        path=home_dir
    obj = Operations(path, key)
    obj.cd()

@app.command()
def cat(path: str = typer.Argument(".")):
    obj=Operations(path)
    obj.cat()

@app.command()
def cp(arg: List[str] = typer.Argument(["."]),
       key: bool = typer.Option(False,"-r")):
    obj=Operations(arg,key)
    obj.cp()

@app.command()
def rm(arg: str = typer.Argument("."),
       key: bool = typer.Option(False,"-r")):
    obj=Operations(arg,key)
    obj.rm()
@app.command()
def mv(arg: List[str] = typer.Argument(["."])):
    obj=Operations(arg)
    obj.mv()

@app.command()
def history(n: int = typer.Argument(0)):
    obj=Operations(n)
    for i in obj.history():
        print(i)
@app.command()
def undo(arg='.'):
    obj=Operations(arg)
    obj.undo()
@app.command()
def zip(path: List[str] = typer.Argument(["."])):
    obj=Operations(path)
    obj.zip()
@app.command()
def unzip(path: str = typer.Argument(".")):
    obj=Operations(path)
    obj.unzip()
@app.command()
def tar(path: List[str] = typer.Argument(["."])):
    obj=Operations(path)
    obj.tar()
@app.command()
def untar(path: str = typer.Argument(".")):
    obj=Operations(path)
    obj.untar()
def main():
    print("q-выход из программы. Вводите команду")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_path = os.path.join(script_dir, '.history')
    with open(history_path,'w',encoding='utf-8') as f:
        f.write('HISTORY\n')
    f.close()
    count=1
    try:
        while True:
            try:
                start_str=input(f"{os.getcwd()}>")

                if start_str=='q':
                    logger.info("Program terminated by user")
                    break
                if not start_str:
                    logger.info("empty enter")
                    continue
                if '\\' in start_str:
                    start_str = start_str.replace('\\','//')
                checked_str=input_check(start_str)
                with open(history_path,'a',encoding='utf-8') as f:
                    if checked_str=='':
                        f.write(f"{count} {start_str}\n")
                        count+=1
                        continue
                    else:
                        f.write(f"{count} {checked_str}\n")
                        count+=1
                command=shlex.split(checked_str)
                if command:
                    app(command,standalone_mode=False)
            except SystemExit:
                pass
            except Exception as e:
                logger.error(f"Error in main {e}")
    except KeyboardInterrupt:
        logger.info("Program terminated by KeyboardInterrupt")

if __name__ == "__main__":
    main()

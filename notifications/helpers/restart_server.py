
import subprocess
import shutil
import sys
import os
import signal

def stop_uvicorn():
    print("Stopping uvicorn...")
    try:
        if os.name == "nt":  
            subprocess.run(["taskkill", "/F", "/IM", "uvicorn.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print("No uvicorn process found or error:", e)

def remove_staticfiles():
    path = "staticfiles"
    if os.path.exists(path):
        print("Removing staticfiles folder...")
        shutil.rmtree(path)
    else:
        print("No staticfiles folder found.")

def collect_static():
    print("Collecting static files...")
    subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"])

def start_uvicorn():
    print("Starting uvicorn server...")
    if os.name == "nt":
        subprocess.Popen(["uvicorn", "social_network.asgi:application", "--reload"], shell=True)

if __name__ == "__main__":
    stop_uvicorn()
    remove_staticfiles()
    collect_static()
    start_uvicorn()
    print("Done!")


# path to activate "python notifications\helpers\restart_server.py"        
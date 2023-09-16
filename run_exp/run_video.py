import os
import sys
import signal
import subprocess
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from pyvirtualdisplay import Display
from time import sleep

IP = "192.168.1.132"  # hostname -I
RUN_TIME_IN_SEC = 320
PROJECT_BASE_DIR = os.getcwd()


def run_abr_server(abr_algo, trace_file):
    if abr_algo == "TEST":
        command = f'exec python {os.path.join(PROJECT_BASE_DIR, "rl_server/test_server.py")} {trace_file}'
    elif abr_algo == "RL":
        command = (
            "exec /usr/bin/python ../rl_server/rl_server_no_training.py " + trace_file
        )
    elif abr_algo == "fastMPC":
        command = "exec /usr/bin/python ../rl_server/mpc_server.py " + trace_file
    elif abr_algo == "robustMPC":
        command = "exec /usr/bin/python ../rl_server/robust_mpc_server.py " + trace_file
    else:
        command = (
            "exec python ../rl_server/simple_server.py " + abr_algo + " " + trace_file
        )

    return subprocess.Popen(command, shell=True)


def get_driver(abr_algo):
    default_chrome_user_dir = os.path.join(
        PROJECT_BASE_DIR, "abr_browser_dir/chrome_data_dir"
    )
    chrome_user_dir = "/tmp/chrome_user_dir_id_" + abr_algo
    os.system("rm -r " + chrome_user_dir)
    os.system("cp -r " + default_chrome_user_dir + " " + chrome_user_dir)

    options = ChromeOptions()
    options.add_argument("--user-data-dir=" + chrome_user_dir)
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=800x600")
    options.add_argument("--headless")

    chrome_driver_path = os.path.join(
        PROJECT_BASE_DIR, "chromedriver-linux64/chromedriver"
    )
    service = Service(executable_path=chrome_driver_path)

    driver = Chrome(service=service, options=options)

    return driver


def run_video(driver: Chrome, abr_algo):
    driver.set_page_load_timeout(10)

    # RL in url because it implements cilent-server as we want
    url = "http://" + IP + "/" + "myindex_" + "RL" + ".html"

    driver.get(url)
    sleep(RUN_TIME_IN_SEC)


def main():
    abr_server_proc = None
    driver = None

    try:
        abr_algo = sys.argv[1]
        trace_file = sys.argv[2]

        abr_server_proc = run_abr_server(abr_algo, trace_file)
        sleep(2)
        driver = get_driver(abr_algo)

        run_video(driver, abr_algo)
    finally:
        if driver is not None:
            driver.quit()
        if abr_server_proc is not None:
            abr_server_proc.send_signal(signal.SIGINT)


if __name__ == "__main__":
    main()

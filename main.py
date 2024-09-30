import os
import sys
import subprocess
from datetime import datetime
import logging
import glob
import time
import pandas as pd
import re



LOG_FILE = "usb_writeblocker_test_log.txt"

# Fragt nach einem Pfad zum Disk und nach der Operation
def get_user_input():
    disk_path = input("Geben Sie den Pfad zum Disk ein: ")
    operation = input("Geben Sie die Operation ein (run_file_operations oder run_scsi_commands): ")
    return disk_path, operation

# Operationen für die Datenmanipulation

def create_file(file_path, content="This is a test file."):
    try:
        with open(file_path, "w") as file:
            file.write(content)
        logging.info(f"File created: {file_path}")
    except PermissionError as e:
        logging.error(f"Permission denied: {file_path}. {e}")
        print(f"Create file failed. Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"Create file failed. Error: {e}")

def rename_file(original_path, new_path):
    try:
        os.rename(original_path, new_path)
        logging.info(f"File renamed from {original_path} to {new_path}")
    except PermissionError as e:
        logging.error(f"Permission denied: {original_path}. {e}")
        print(f"Rename file failed. Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"Rename file failed. Error: {e}")

def modify_file(file_path, new_content="This is modified content."):
    try:
        with open(file_path, "w") as file:
            file.write(new_content)
        logging.info(f"File modified: {file_path}")
    except PermissionError as e:
        logging.error(f"Permission denied: {file_path}. {e}")
        print(f"Permission denied: {file_path}. {e}")
        print(f"Modify file failed. Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"Modify file failed. Error: {e}")


def delete_file(file_path):
    try:
        os.remove(file_path)
        logging.info(f"File deleted: {file_path}")
    except PermissionError as e:
        logging.error(f"Permission denied: {file_path}. {e}")
        print(f"Permission denied: {file_path}. {e}")
        print(f"Delete file failed. Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"Delete file failed. Error: {e}")

def read_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    logging.info(f"File read: {file_path} with content: {content}")

def change_file_times(file_path):
    try:
        access_time = "2023-01-01 12:00:00"
        modify_time = "2023-01-01 12:30:00"
        # Konvertiert die Zeit in das richtige Format
        atime = time.mktime(time.strptime(access_time, "%Y-%m-%d %H:%M:%S"))
        mtime = time.mktime(time.strptime(modify_time, "%Y-%m-%d %H:%M:%S"))

        #Setzt die Zugriffs- und Änderungszeit der Datei
        os.utime(file_path, (atime, mtime))
        logging.info("Changed modification time of the file")
    
    except PermissionError as e:
        logging.error(f"Permission denied: {file_path}. {e}")
        print(f"Permission denied: {file_path}. {e}")
        print(f"Modify file times failed. Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"Modify file time failed. Error: {e}")
# Operationen für SCSI-Befehle senden


# Nach Integrität prüfen
# MFT ständig prüfen check_mft_change()
# Führt das MFT-Tool aus
def runmftecmd(disk_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mfetcmd_path = os.path.join(script_dir, 'MFTECmd', 'MFTECmd.exe')
    # Pfad zum Ausgabeordner
    output_dir = os.path.join(script_dir, 'outputs')
    
    cmd = mfetcmd_path + ' -f ' + disk_path + '\\$MFT' +  ' --csv ' + output_dir

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    logging.info(f"Run command: {cmd}")
    return result.stdout

# Sucht nach dem Namen der csv Datei mit MFT Einträgen
def extractcsvpath(output):
    match = re.search(r'CSV output will be saved to (.+.csv)', output)
    if match:
        logging.info("Found CSV output path")
        return match.group(1)
    else:
        logging.error("CSV output path not found in the tool's output")
        return 0

# Liest die csv Datei
def read_csv_to_dataframe(csv_path):
    logging.info("Reading CSV to Dataframe...")
    return pd.read_csv(csv_path)

# Vergleicht die csv-Dateien
def compare_csv(old_df, new_df, action):
    logging.info("Comparing dataframes...")

    columns = [
        'LastRecordChange0x10', 'LastRecordChange0x30', 
        'LastAccess0x10', 'LastAccess0x30'
    ]

    old_df = old_df[columns]
    new_df = new_df[columns]
 
    # Sicherstellen, dass beide DataFrames dieselben Indizes und Spalten haben
    if old_df.equals(new_df):
        print(f"No changes found in the MFT after {action} \n")
        logging.info("No changes found")
    else:
        diffs = new_df[~new_df.isin(old_df.to_dict(orient='list')).all(axis=1)]
      
        if diffs.empty:
            print(f"No changes found in the MFT after {action} \n")
            logging.info("No Changes found")
        else:
            print(f"Found changes in the MFT after {action} \n")
            logging.info(f"Changes found in the mft: {diffs}")
    


def check_mft_changes(prev_df, action, disk_path):
    logging.info("Check for MFT Changes...")
    output = runmftecmd(disk_path)
    csvpath = extractcsvpath(output)
    df = read_csv_to_dataframe(csvpath)
    compare_csv(prev_df,df, action)

    return df


# Dateioperationen durchführen 
def run_file_operations(disk_path):
    # Sucht nach einer txt Datei
    search_pattern = os.path.join(disk_path, "*.txt")
    txt_files = glob.glob(search_pattern)
    file_path = txt_files[0]

    # Neuer Name für die Datei
    new_name = "newname.txt"

    # Initialen Zustand der MFT sichern
    output1 = runmftecmd(disk_path)

    csvpath1 = extractcsvpath(output1)
    df1 = read_csv_to_dataframe(csvpath1)

    # Operationen mit der Datei
    read_file(file_path)
    df = check_mft_changes(df1, "reading file", disk_path)
    time.sleep(1)
    # Modifikation der Datei
    modify_file(file_path)
    df = check_mft_changes(df, "modification of the file", disk_path)
    time.sleep(1)
 
    rename_file(file_path, disk_path + new_name)
    df = check_mft_changes(df, "renaming the file", disk_path)
    time.sleep(1)
    delete_file(disk_path + new_name)
    df = check_mft_changes(df, "deleting the file", disk_path)
    time.sleep(1)
    create_file(disk_path + "newfile.txt")
    df = check_mft_changes(df, "creating a new file", disk_path)
    time.sleep(1)
    change_file_times(disk_path + "newfile.txt")
    df = check_mft_changes(df, "changing the metadata of the newfile", disk_path)

    return 1

# SCSI-Befehle senden
def run_scsi_commands(device):
    return 1


# Abfrage welche Operation
if __name__ == "__main__":
    if len(sys.argv) < 3:
        disk_path, operation = get_user_input()
    else:
        disk_path = sys.argv[1]
        operation = sys.argv[2] 

    # Eine neue Log-Datei wird erstellt
    # Aktuelle Datum und Uhrzeit 
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Dateiname mit Datum und Uhrzeit
    log_filename = os.path.join("logs", f"logfile_{current_time}.log")

    # Logging-Konfiguration
    logging.basicConfig(
        filename=log_filename,
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info("Starting WriteBlocker tests...")

    # Je nach gewählten Operation, starten die Tests
    if operation == "run_file_operations":
        run_file_operations(disk_path)
    elif operation == "run_scsi_commands":
        run_scsi_commands(disk_path)
    else:
        logging.error("Invalid operation specified")

    logging.info("WriteBlocker tests completed")
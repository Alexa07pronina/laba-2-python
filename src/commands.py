import os
import pathlib
import stat
import shutil
import shlex
import zipfile
import tarfile
from src.logger import get_logger

logger = get_logger()

script_dir = os.path.dirname(os.path.abspath(__file__))
history_path = os.path.join(script_dir, '.history')
base_dir = os.path.dirname(script_dir)
trash_path = os.path.join(base_dir, ".trash")

home_dir=os.path.expanduser("~")
home_dir=home_dir.replace('\\','//')
parent_dir_for_home= os.path.dirname(home_dir)

if not os.path.exists(trash_path):
    os.mkdir(trash_path)

protected_paths = [
            os.path.abspath(home_dir),
            os.path.abspath(base_dir),
            os.path.abspath(script_dir),
            os.path.abspath(trash_path),
            os.path.abspath(history_path),
            os.path.abspath(os.getcwd()),
            os.path.abspath(parent_dir_for_home)
]

def input_check(string: str) -> str:
    """
    Проверка корректности введеной строки и преобразование относительных путей в абсолютные
    """
    lst=shlex.split(string)
    if lst[0] not in ['cp','rm','ls','mv','history','undo','cd','cat','untar','unzip','tar','zip']:
        logger.error(f"Wrong input: No such command {lst[0]}")
        return ""

    if len(lst)>1:
        if lst[1] in ["-r","-l"]:
            if lst[0] in ['cd','ls','history','undo','cat','untar','unzip','tar','zip'] and lst[1]=="-r":
                logger.error(f"Wrong input: No such key for command {lst[0]}")
                return ""
            elif lst[0] in ['cp','rm','mv','history','undo','cd','cat','untar','unzip','tar','zip'] and lst[1]=="-l":
                logger.error(f"Wrong input: No such key for command {lst[0]}")
                return ""
            if lst[0] in ['cp','mv'] and len(lst)!=4:
                logger.error(f"Wrong input: Missing arguments")
                return ""
        elif lst[1][0]=='-':
            logger.error(f"Wrong input: No such key {lst[1]}")
            return ""
        elif len(lst)!=3 and lst[0] in ['cp','mv','zip','tar']:
            logger.error(f"Wrong input: Missing arguments")
            return ""

        if len(lst)>=2:
            if lst[0] in ['history','untar','unzip'] and len(lst)==2:
                return string
            if lst[0] in ['zip','tar']:
                lst[1] = f'"{os.path.abspath(lst[1])}"'
                lst[1] = lst[1].replace('\\', '//')
                return " ".join(lst)
            try:
                for i in range(1,len(lst)):
                    if lst[i] not in ['-l','-r']:
                        if os.path.exists(os.path.abspath(lst[i])):
                            lst[i]=f'"{os.path.abspath(lst[i])}"'
                            lst[i]=lst[i].replace('\\','//')
                        elif lst[i]=="~":
                            lst[i]=home_dir
                        else:
                            logger.error(f"Path do not exists")
                            return ""
                return " ".join(lst)
            except Exception as a:
                logger.error(f"Wrong input: {e}")
                return ""
        else:
            return " ".join(lst)
    else:
        if lst[0] in ['ls','undo']:
            return string
        else:
            logger.error(f"missing arguments")
            return ""

class Operations:
    def __init__(self,arg,key=False):
        self.arg = arg
        self.key = key

    def history(self):
        """
        Отображение последних n введенных команд
        """
        try:
            f=open(history_path,encoding='utf-8')
            a=[]
            for s in f:
                a.append(s.rstrip())
            f.close()
            logger.info(f"history {self.arg}: SUCCESS\n")
            if self.arg>= len(a):
                return a[:-1]
            return a[-self.arg-1:-1]
        except Exception as e:
            logger.error(f"Error in history: {e}")

    def ls(self):
        """
        Отображение всех файлов и каталогов по указанному пути
        """
        try:
            files = os.listdir(self.arg)
            if self.key==False:
                logger.info(f"ls {self.arg}: SUCCESS\n")
                return files
            result = []

            for file in files:
                full_path = os.path.join(self.arg, file)
                stat_info = os.stat(full_path)
                permissions = stat.filemode(stat_info.st_mode)
                size = stat_info.st_size
                time= stat_info.st_mtime
                if os.path.isdir(file):
                    result.append(f"{permissions} {time} {size:8d} \033[94m{file}\033[0m")
                else:
                    result.append(f"{permissions} {time} {size:8d} {file}")
            logger.info(f"ls -l {self.arg}: SUCCESS\n")
            return result

        except Exception as e:
            logger.error(f"Error in ls: {e}")
            return []

    def cd(self):
        """
        Перемещение по файловой системе
        """
        try:
            os.chdir(self.arg)
            logger.info(f"cd {self.arg}: SUCCESS\n")
        except Exception as e:
            logger.error(f"Error in cd: {e}")

    def cat(self):
        """
        Вывод содержимого файла
        """
        if self.arg==".":
            logger.warning("Attempted to cat current directory")
            print("path is not found")
            return None
        try:
            with open(self.arg, 'r', encoding='utf-8') as file:
                content = file.read()
                print(content)
            logger.info(f"cat {self.arg}: SUCCESS\n")
        except Exception as e:
            logger.error(f"Error in cat: {e}")

    def cp(self):
        """
        Копирование файла или директории
        """
        arg1, arg2 = self.arg[0], self.arg[1]
        parent_dir = os.path.dirname(arg1)
        protected_paths.append(os.path.abspath(parent_dir))
        protected_paths.append(os.getcwd())
        if os.path.abspath(arg1) in protected_paths or os.path.dirname(
                os.path.abspath(arg1)).lower() == os.path.abspath(parent_dir_for_home).lower():
            logger.warning(f"Attempted to delete protected directory: {arg1}")
            print("Permission denied")
            return None
        try:
            arg1,arg2=self.arg[0],self.arg[1]
            if os.path.exists(arg1):
                if os.path.isfile(arg1):
                    destination = os.path.join(arg2, os.path.basename(arg1))
                    counter = 1
                    while os.path.exists(destination):
                        name, ext = os.path.splitext(os.path.basename(arg1))
                        destination = os.path.join(arg2, f"{name}_{counter}{ext}")
                        counter += 1
                    shutil.copy2(arg1, destination)
                    logger.info(f"Copy file {arg1} to {arg2}")

                elif os.path.isdir(arg1):
                    destination = os.path.join(arg2, os.path.basename(arg1))
                    counter = 1
                    while os.path.exists(destination):
                        destination = os.path.join(arg2, f"{os.path.basename(arg1)}_{counter}")
                        counter += 1

                    if self.key == True:
                        shutil.copytree(arg1, destination)
                        logger.info(f"Copy directory to {destination}")
                    else:
                        logger.warning("For directory use -r")
                        return None

                logger.info(f"cp {self.arg}: SUCCESS\n")
            else:
                logger.warning(f"Path does not exist: {path}")
        except Exception as e:
            logger.error(f"Error in cp: {e}")

    def rm(self):
        """
        Удаление файлов и директорий
        """
        path = self.arg
        parent_dir = os.path.dirname(path)
        protected_paths.append(os.path.abspath(parent_dir))
        protected_paths.append(os.getcwd())
        if os.path.abspath(path) in protected_paths or os.path.dirname(os.path.abspath(path)).lower() == os.path.abspath(parent_dir_for_home).lower():
            logger.warning(f"Attempted to delete protected directory: {path}")
            print("Permission denied")
            return None

        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    destination = os.path.join(trash_path, os.path.basename(path))
                    counter = 1
                    while os.path.exists(destination):
                        name, ext = os.path.splitext(os.path.basename(path))
                        destination = os.path.join(trash_path, f"{name}_{counter}{ext}")
                        counter += 1
                    shutil.move(path, destination)
                    logger.info(f"Moved file to trash: {path}")

                elif os.path.isdir(path):
                    ans = input("Удалить каталог? y/n\n")
                    if ans != 'y':
                        return None

                    destination = os.path.join(trash_path, os.path.basename(path))
                    counter = 1
                    while os.path.exists(destination):
                        destination = os.path.join(trash_path, f"{os.path.basename(path)}_{counter}")
                        counter += 1

                    if not os.listdir(path):
                        shutil.move(path, destination)
                        logger.info(f"Moved empty directory to trash: {path}")
                    else:
                        if self.key == True:
                            shutil.move(path, destination)
                            logger.info(f"Moved directory to trash: {path}")
                        else:
                            logger.warning("For directory use -r")
                            return None

                logger.info(f"rm {self.arg}: SUCCESS\n")
            else:
                logger.warning(f"Path does not exist: {path}")
        except Exception as e:
            logger.error(f"Error in rm: {e}")

    def mv(self):
        """
        Перемещение файлов и директорий
        """
        try:
            arg1, arg2 = self.arg[0], self.arg[1]
            parent_dir = os.path.dirname(arg1)
            protected_paths.append(os.path.abspath(parent_dir))
            protected_paths.append(os.getcwd())
            if os.path.abspath(arg1) in protected_paths or os.path.dirname(
                    os.path.abspath(arg1)).lower() == os.path.abspath(parent_dir_for_home).lower():
                logger.warning(f"Attempted to delete protected directory: {arg1}")
                print("Permission denied")
                return None

            if os.path.exists(arg1):
                if os.path.isfile(arg1):
                    destination = os.path.join(arg2, os.path.basename(arg1))
                    counter = 1
                    while os.path.exists(destination):
                        name, ext = os.path.splitext(os.path.basename(arg1))
                        destination = os.path.join(arg2, f"{name}_{counter}{ext}")
                        counter += 1
                    shutil.move(arg1, destination)
                    logger.info(f"Moved file {arg1} to {arg2}")

                elif os.path.isdir(arg1):
                    destination = os.path.join(arg2, os.path.basename(arg1))
                    counter = 1
                    while os.path.exists(destination):
                        destination = os.path.join(arg2, f"{os.path.basename(arg1)}_{counter}")
                        counter += 1
                    shutil.move(arg1, destination)
                    logger.info(f"Moved directory {arg1} to {arg2}")

                logger.info(f"mv {self.arg}: SUCCESS\n")
            else:
                logger.warning(f"Path does not exist: {arg1}")
        except Exception as e:
            logger.error(f"Error in mv: {e}")

    def undo(self):
        """
        Отмена действия cp,rm,mv
        """
        try:
            f=open(history_path,encoding='utf-8')
            a=[]
            for s in f:
                a.append(s.rstrip())
            f=0
            for i in range(len(a)-1,1,-1):
                command = shlex.split(a[i])
                if command[1]=='mv':
                    f = 1
                    arg1=os.path.join(command[3],os.path.basename(command[2]))
                    arg2=os.path.dirname(command[2])
                    self.arg = [arg1, arg2]
                    self.mv()
                    break
                elif command[1]=='rm':
                    f=1
                    if command[2][0]!='-':
                        arg1=os.path.join(trash_path,os.path.basename(command[2]))
                        arg2=os.path.dirname(command[2])
                    else:
                        arg1 = os.path.join(trash_path, os.path.basename(command[3]))
                        arg2 = os.path.dirname(command[3])
                    self.arg=[arg1,arg2]
                    self.mv()
                elif command[1] == 'cp':
                    f=1
                    if command[1]=='-r':
                        arg1 = os.path.join(command[4], os.path.basename(command[3]))
                        arg2 = os.path.dirname(command[3])
                    else:
                        arg1 = os.path.join(command[3], os.path.basename(command[2]))
                        arg2 = os.path.dirname(command[2])
                    if os.path.isdir(arg1):
                        shutil.rmtree(arg1)
                    else:
                        os.remove(arg1)
                    break
            if f==0:
                logger.warning("no commands to cancel")
        except Exception as e:
            logger.error(f"Error in undo: {e}")

    def zip(self):
        """
        Создание zip-архива с указанным именем
        """
        arg1, arg2 = self.arg[0], self.arg[1]

        try:
            parent_dir = os.path.dirname(os.path.abspath(arg1))

            if arg2.endswith('.zip'):
                zip_name = arg2
            else:
                zip_name = f"{arg2}.zip"

            zip_path = os.path.join(parent_dir, zip_name)

            if not os.path.exists(arg1):
                logger.error(f"{arg1} not found")
                return None

            if not os.path.isdir(arg1):
                logger.error(f"{arg1} is not a folder")
                return None

            if not any(os.scandir(arg1)):
                logger.error(f"directory {arg1} is empty")
                return None

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(arg1):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, arg1)
                        zipf.write(file_path, arcname)

            logger.info(f"ZIP Create: SUCCESS - {zip_path}")
            return zip_path

        except Exception as e:
            logger.error(f"error in zip: {e}")
            return None

    def tar(self):
        """
        Создание tar-архива с указанным именем
        """
        arg1, arg2 = self.arg[0], self.arg[1]

        try:
            parent_dir = os.path.dirname(os.path.abspath(arg1))

            if arg2.endswith('.tar.gz'):
                tar_name = arg2
            else:
                tar_name = f"{arg2}.tar.gz"

            tar_path = os.path.join(parent_dir, tar_name)

            if not os.path.exists(arg1):
                logger.error(f"{arg1} not found")
                return None

            if not os.path.isdir(arg1):
                logger.error(f"{arg1} is not a folder")
                return None

            # Проверяем, что папка не пустая
            if not any(os.scandir(arg1)):
                logger.error(f"directory {arg1} is empty")
                return None

            # Создаем архив
            with tarfile.open(tar_path, 'w:gz') as tarf:
                tarf.add(arg1, arcname=os.path.basename(arg1))

            logger.info(f"TAR Create: SUCCESS -> {tar_path}")
            return tar_path

        except Exception as e:
            logger.error(f"Error in create tar: {e}")
            return None

    def unzip(self):
        """
        Распаковка zip-архива в папку с именем архива
        """
        archive_path = self.arg

        try:
            current_dir = os.path.abspath('.')
            archive_abs_path = os.path.abspath(archive_path)
            if not os.path.exists(archive_abs_path):
                logger.error(f"Archive not found: {archive_abs_path}")
                return None

            if not zipfile.is_zipfile(archive_abs_path):
                logger.error(f"Not a zip file: {archive_abs_path}")
                return None

            archive_name = os.path.basename(archive_abs_path)
            folder_name = os.path.splitext(archive_name)[0]
            extract_dir = os.path.join(current_dir, folder_name)

            os.makedirs(extract_dir, exist_ok=True)

            with zipfile.ZipFile(archive_abs_path, 'r') as zipf:
                zipf.extractall(extract_dir)

            logger.info(f"Unzip SUCCESS -> {extract_dir}")
            return extract_dir

        except Exception as e:
            logger.error(f"Error in unzip: {e}")
            return None

    def untar(self):
        """
        Распаковка tar-архива в папку с именем архива
        """
        archive_path = self.arg

        try:
            current_dir = os.path.abspath('.')
            archive_abs_path = os.path.abspath(archive_path)

            if not os.path.exists(archive_abs_path):
                logger.error(f"Archive not found: {archive_abs_path}")
                return None

            archive_name = os.path.basename(archive_abs_path)
            folder_name = archive_name[:-7]
            extract_dir = os.path.join(current_dir, folder_name)

            os.makedirs(extract_dir, exist_ok=True)

            with tarfile.open(archive_abs_path, 'r:gz') as tarf:
                tarf.extractall(extract_dir)

            logger.info(f"Untar SUCCESS -> {extract_dir}")
            return extract_dir

        except Exception as e:
            logger.error(f"Error in untar: {e}")
            return None
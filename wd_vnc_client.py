from time import sleep
import paramiko as pm
import subprocess
from multiprocessing import Process,Manager
from sys import argv
import easygui,tempfile

# shared_vars = Manager().dict()
# ssh_host_ip = None


class WdVncClient():
    ssh_username = "arch"
    remote_display_port = ":0"
    vncrfbport = 5923
    
    # client_path = '"C:\\Program Files\\RealVNC\\VNC Viewer\\vncviewer.exe"'
    @classmethod
    def init(cls,ip_suffix):
        print("initializing ssh client")
        cls.ssh_host_ip="192.168."+ip_suffix
        digits=str(cls.ssh_host_ip).split(".")
        if len(digits)!=4:
            raise Exception("Invalid Ip Adress")
        for i in digits:
            if not i.isdigit() or int(i)>255:
                raise Exception("Invalid Ip Adress")
    @classmethod
    def forwardVncPort(cls,ip_suffix):
        cls.init(ip_suffix)
        print("forwarding a port")
        port_forward_str = f"{cls.vncrfbport}:localhost:{cls.vncrfbport}"
        login_str = f"{cls.ssh_username}@{cls.ssh_host_ip}"
        cmd_line = ["ssh","-f","-N","-L",port_forward_str,login_str]
        subprocess.run(cmd_line)
        
    @classmethod
    def startRemoteVncServer(cls,ip_suffix):
        cls.init(ip_suffix)
        print("Starting WdVnc server",cls.ssh_host_ip)
        
        ssh_client = pm.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.connect(cls.ssh_host_ip, key_filename="C:\\Users\\Harsh\\.ssh\\id_rsa.pub",username=cls.ssh_username,look_for_keys=True)
        
        if(not ssh_client.get_transport().is_alive()):
            raise Exception("Failed initializing client")
        ret = ssh_client.exec_command("python3 /common/ws_internal/wd_vnc/wd_vnc_server.py start",get_pty=True,environment={"DISPLAY":cls.remote_display_port})
        if ret[1].channel.recv_exit_status() !=0:
            raise Exception("Failed starting server\n"+ret[1].read().decode()+ret[2].read().decode())

    @classmethod
    def startVncClient(cls,ip_suffix):
        cls.init(ip_suffix)
        sleep(4)
        print("Starting WdVnc client")
        cmd_line = ["vncviewer","localhost:"+str(cls.vncrfbport),"-FullScreen"]
        if subprocess.run(cmd_line).returncode!=0:
            raise Exception("Failed starting client")

if __name__=="__main__":
    ip_suffix = easygui.enterbox("Enter IP suffix digits","WdVncClient",strip=True,default="0.0")
    WdVncClient.init(ip_suffix)
    WdVncProcList = [WdVncClient.forwardVncPort,
        WdVncClient.startRemoteVncServer,WdVncClient.startVncClient]
    WdVncProcHandlers = list()
    for proc in WdVncProcList:
        p = Process(target=proc,args=(ip_suffix,))
        p.start()
        WdVncProcHandlers.append(p)
    WdVncProcHandlers.reverse()
    for p in WdVncProcHandlers[:-1]:
        p.join()
    WdVncProcHandlers[-1].kill()

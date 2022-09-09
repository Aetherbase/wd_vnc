#!/usr/bin/env python3
from logging import raiseExceptions
from Xlib.ext import randr
import subprocess
class WdVncServer():
    display_port_name = "HDMI-A-0"
    resolution_tup = (1620,1080)
    display_mode_name = None
    place_wrt_main_dp="left-of"
    clip_suffix="-1920+0"
    main_display_port_name = "eDP"
    main_display_port = ":0"
    tcp_rfb_port = 5923
    @classmethod
    def fetchModeFromResolution(cls):
        cvt_out = subprocess.run(['cvt', str(cls.resolution_tup[0]), str(cls.resolution_tup[1])], stdout=subprocess.PIPE).stdout.decode()
        cvt_lines = cvt_out.splitlines()
        modeline = None
        modeline_str = "Modeline"
        for cvt_line in cvt_lines:
            if cvt_line.startswith(modeline_str):
                modeline = cvt_line[len(modeline_str)+1:]
        if isinstance(modeline,str):
            mode_args = modeline.split(" ")
            filtered_mode_args = [i for i in mode_args if i!= '']
            cls.display_mode_name = filtered_mode_args[0]
            return filtered_mode_args
        else:
            raise Exception("Invalid Mode Config") 

    @classmethod
    def createDisplayModeXrandr(cls):
        mode_args = cls.fetchModeFromResolution()
        confirm_cmd_line = ["xrandr"]
        confirm_lines = subprocess.run(confirm_cmd_line,stdout=subprocess.PIPE).stdout.decode().strip().splitlines()
        already_created = False
        for c_line in confirm_lines:
            if c_line.strip().startswith(cls.display_mode_name):
                already_created = True
        if already_created:
            return
        cmd_line = [ "xrandr","--newmode"]
        cmd_line.extend(mode_args)
        status = subprocess.run(cmd_line).returncode
        if status!=0:
            raise Exception("Error while creating mode")
    
    @classmethod
    def addModeToXrandrDisplayPort(cls):
        add_cmd_line = ["xrandr","--addmode",cls.display_port_name,cls.display_mode_name]
        if subprocess.run(add_cmd_line).returncode != 0 :
            raise Exception(f"Unable to add {cls.display_mode_name} mode to Xrandr port {cls.display_port_name}.")
        config_cmd_line = ["xrandr","--output",cls.display_port_name,"--mode",cls.display_mode_name,f"--{cls.place_wrt_main_dp}",cls.main_display_port_name]
        if subprocess.run(config_cmd_line).returncode != 0 :
            raise Exception(f"Unable to configure {cls.display_mode_name} mode of Xrandr port {cls.display_port_name}.")
    
    @classmethod
    def delModeFromXrandrPort(cls):
        config_cmd_line = ["xrandr","--output",cls.display_port_name,"--off"]
        if subprocess.run(config_cmd_line).returncode != 0 :
            raise Exception(f"Unable to turn off {cls.display_mode_name} mode of Xrandr port {cls.display_port_name}.")
        del_cmd_line = ["xrandr","--delmode",cls.display_port_name,cls.display_mode_name]
        if subprocess.run(del_cmd_line).returncode != 0 :
            raise Exception(f"Unable to delete {cls.display_mode_name} mode from Xrandr port {cls.display_port_name}.")

    @classmethod
    def startVncServer(cls):
        clip_str = f"{cls.resolution_tup[0]}x{cls.resolution_tup[1]}{cls.clip_suffix}"
        vnc_cmd_line = ["x11vnc","-localhost","-display",cls.main_display_port,"-clip", clip_str,"-rfbport",str(cls.tcp_rfb_port)]
        subprocess.run(vnc_cmd_line)

if __name__=='__main__':
    WdVncServer.createDisplayModeXrandr()
    WdVncServer.addModeToXrandrDisplayPort()
    WdVncServer.startVncServer()
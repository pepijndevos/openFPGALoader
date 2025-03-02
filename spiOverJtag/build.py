#!/usr/bin/env python3
from edalize import get_edatool
import os

if len(os.sys.argv) != 2:
    print("missing board param")
    os.sys.exit()
part = os.sys.argv[1]

build_dir="tmp_" + part
if not os.path.isdir(build_dir):
    try:
        os.mkdir(build_dir)
    except OSError:
        print ("Creation of the directory %s failed" % build_dir)
    else:
        print ("Successfully created the directory %s " % build_dir)

currDir = os.path.abspath(os.path.curdir) + '/'
files = []
parameters = {}

subpart = part[0:4].lower()
if subpart == '10cl':
    family = "Cyclone 10 LP"
    tool = "quartus"
elif subpart == 'ep4c':
    family = "Cyclone IV E"
    tool = "quartus"
elif subpart[0:2] == '5c':
    family = "Cyclone V"
    tool = "quartus"
    files.append({'name': currDir + 'constr_cycloneV.tcl',
                  'file_type': 'tclSource'})
elif subpart == "xc7a":
    family = "Artix"
    tool = "vivado"
elif subpart == "xc7k":
    family = "Kintex 7"
    tool = "vivado"
elif subpart == "xc7s":
    family = "Spartan 7"
    tool = "vivado"
elif subpart == "xc6s":
    family = "Spartan6"
    tool = "ise"
else:
    print("Error: unknown device")
    os.sys.exit()

if tool in ["ise", "vivado"]:
    pkg_name = {
        "xc6slx16ftg256"   : "xc6s_ftg256",
        "xc6slx16csg324"   : "xc6s_csg324",
        "xc6slx45csg324"   : "xc6s_csg324",
        "xc6slx100fgg484"  : "xc6s_fgg484",
        "xc7a35tcpg236"    : "xc7a_cpg236",
        "xc7a35tcsg324"    : "xc7a_csg324",
        "xc7a35tftg256"    : "xc7a_ftg256",
        "xc7a50tcpg236"    : "xc7a_cpg236",
        "xc7a75tfgg484"    : "xc7a_fgg484",
        "xc7a100tcsg324"   : "xc7a_csg324",
        "xc7a100tfgg484"   : "xc7a_fgg484",
        "xc7a200tsbg484"   : "xc7a_sbg484",
        "xc7a200tfbg484"   : "xc7a_fbg484",
        "xc7k325tffg676"   : "xc7k_ffg676",
        "xc7k325tffg900"   : "xc7k_ffg900",
        "xc7s25csga324"    : "xc7s_csga324",
        "xc7s50csga324"    : "xc7s_csga324"
        }[part]
    if tool == "ise":
        cst_type = "UCF"
        tool_options = {'family': family,
                        'device': {
                            "xc6slx16ftg256": "xc6slx16",
                            "xc6slx16csg324": "xc6slx16",
                            "xc6slx45csg324": "xc6slx45",
                            "xc6slx100fgg484": "xc6slx100"}[part],
                        'package': {
                            "xc6slx16ftg256": "ftg256",
                            "xc6slx16csg324": "csg324",
                            "xc6slx45csg324": "csg324",
                            "xc6slx100fgg484": "fgg384"}[part],
                        'speed' : -3
                }
    else:
        cst_type = "xdc"
        tool_options = {'part': part+ '-1'}
    cst_file = currDir + "constr_" + pkg_name + "." + cst_type.lower()
    files.append({'name': currDir + 'xilinx_spiOverJtag.v',
                  'file_type': 'verilogSource'})
    files.append({'name': cst_file, 'file_type': cst_type})
else:
    full_part = {
        "10cl025256": "10CL025YU256C8G",
        "ep4ce2217" : "EP4CE22F17C6",
        "ep4ce1523" : "EP4CE15F23C8",
        "5ce223"    : "5CEFA2F23I7",
        "5ce423"    : "5CEBA4F23C8",
        "5cse423"   : "5CSEMA4U23C6",
        "5cse623"   : "5CSEBA6U23I7"}[part]
    files.append({'name': currDir + 'altera_spiOverJtag.v',
                  'file_type': 'verilogSource'})
    files.append({'name': currDir + 'altera_spiOverJtag.sdc',
                  'file_type': 'SDC'})
    tool_options = {'device': full_part, 'family':family}

parameters[family.lower().replace(' ', '')]= {
    'datatype': 'int',
    'paramtype': 'vlogdefine',
    'description': 'fpga family',
    'default': 1}

edam = {'name' : "spiOverJtag",
        'files': files,
        'tool_options': {tool: tool_options},
        'parameters': parameters,
        'toplevel' : 'spiOverJtag',
}

backend = get_edatool(tool)(edam=edam, work_root=build_dir)
backend.configure()
backend.build()

if tool == "vivado":
    import shutil
    shutil.copy("tmp_" + part + "/spiOverJtag.runs/impl_1/spiOverJtag.bit",
            "tmp_" + part);

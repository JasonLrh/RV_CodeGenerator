import json
import sys
import os
from click import echo

from numpy import product

import Variable


class fileWriter:
    SEPERATOR = '/'

    def __init__(self, rootPath=None) -> None:
        if rootPath == None:
            self.root = './'
        else:
            self.root = rootPath

    def WriteFile(self, fileName: str, content: str):
        fName = self.root + self.SEPERATOR + fileName
        os.makedirs(os.path.dirname(fName), exist_ok=True)
        print(fName)
        with open(fName, "w") as f:
            f.write(content)


def headerFileGenerator(name: str, license="") -> dict:
    name = name

    FILE_DEFS = name.upper() + '_H'
    return {
        "begin": '''\
%s
#ifndef %s
#define %s

#ifdef __cplusplus
extern "C" {
#endif

''' % (license, FILE_DEFS, FILE_DEFS),
        "end": '''\

#ifdef __cplusplus
}
#endif
#endif // EOF
'''
    }


class fileGenerator:
    def __init__(self, rootPath=None) -> None:
        if rootPath != None:
            if os.path.exists(rootPath) == False:
                os.mkdir(rootPath)
        self.fileWriter = fileWriter(rootPath)

        self.lisence = Variable.LISENCE

    def genBaseLib(self):
        baseRootPath = 'Drivers/BaseLib/'
        # Drivers/BaseLib/Include/general_system.h
        dirPath = "Include/"
        ffffffff = 'general_system'
        structHeaderFile = headerFileGenerator(ffffffff, self.lisence)
        content = structHeaderFile["begin"] + \
            Variable.F_GENERAL_SYSTEM_H + structHeaderFile["end"]
        self.fileWriter.WriteFile(
            baseRootPath + dirPath + ffffffff + '.h', content)

        # Device/Include
        dirPath = "Device/Include/"
        ffffffff = self.BigName.lower() + 'xx'
        structHeaderFile = headerFileGenerator(ffffffff, self.lisence)
        raw = '''\
#if 0
'''
        for product_name in self.product_names:
            vaName = self.BigName+product_name
            raw += '''\
#elif defined(%s)
#include "%s.h"
''' % (vaName.upper(), vaName.lower())

        raw += "#endif\n"

        content = structHeaderFile["begin"] + raw + structHeaderFile["end"]
        self.fileWriter.WriteFile(
            baseRootPath + dirPath + ffffffff + '.h', content)

        for product_name in self.product_names:
            ffffffff = self.BigName.lower() + product_name.lower()
            structHeaderFile = headerFileGenerator(
                ffffffff, self.lisence)

            raw = '''\
#include "general_system.h"
'''
            per_kind = []
            for echProduct in self.__product_struct:
                if echProduct['name'] == product_name:
                    ks = echProduct['per']
                    for kkk in ks:
                        pertype = kkk['type'].upper()
                        if pertype not in per_kind:
                            per_kind.append(pertype)
                    break

            typedef_struct_strs = ""
            for selfper in per_kind:
                reg_info = None

                break_flag = False
                for echStructure in self.__perip_struct:
                    if selfper == echStructure['name'].upper():
                        reg_info = echStructure['reg']
                        break_flag = True
                        break

                if break_flag == False:
                    print(f"err: per ({selfper}) not in per_info.json")
                    exit(1)
                val_str = "typedef struct {\n"
                for regName in reg_info:
                    val_str += "  __IO uint32_t %s;\n" % (regName.upper())
                val_str += "} %s_TypeDef;\n" % (selfper)
                typedef_struct_strs += val_str + "\n"

            raw += typedef_struct_strs

            # TODO : add defines to register #define TIM1 ((TIM_Typedef))

            content = structHeaderFile["begin"] + raw + structHeaderFile["end"]
            fileName = baseRootPath + dirPath + ffffffff + '.h'
            self.fileWriter.WriteFile(fileName, content)

    def genHalLib(self):
        def hal_module_name_generator(module_name:str) -> str:
            nnn = self.BigName.lower()+'xx_hal'
            if module_name == "":
              return nnn
            else:
              nnn += "_" + module_name.lower()
              return nnn
        
        baseRootPath = 'Drivers/%s_HAL_Driver/'%(self.BigName.upper())
        dirPath = "Inc/"
        ffffffff = hal_module_name_generator('def')
        structHeaderFile = headerFileGenerator(ffffffff, self.lisence)
        content = structHeaderFile["begin"] + \
            Variable.F_HAL_DEF_H + structHeaderFile["end"]
        self.fileWriter.WriteFile(
            baseRootPath + dirPath + ffffffff + '.h', content)

        ffffffff = hal_module_name_generator("")
        structHeaderFile = headerFileGenerator(ffffffff, self.lisence)
        content = structHeaderFile["begin"] + \
            "#include \"rv32_hal_conf.h\"\n" + structHeaderFile["end"]
        self.fileWriter.WriteFile(
            baseRootPath + dirPath + ffffffff + '.h', content)
        for per in self.__perip_struct:
            dirPath = "Inc/"
            ffffffff = hal_module_name_generator(per['name'].lower())
            structHeaderFile = headerFileGenerator(ffffffff, self.lisence)
            raw = Variable.getHAL_per_h(per['name'])
            content = structHeaderFile["begin"] + \
                raw + structHeaderFile["end"]
            self.fileWriter.WriteFile(
                baseRootPath + dirPath + ffffffff + '.h', content)

            dirPath = "Src/"
            ffffffff = hal_module_name_generator(per['name'].lower())
            content =  self.lisence + '''\
#include "rv32f0xx_hal.h"
#ifdef HAL_%s_MODULE_ENABLED

#endif
'''%(per['name'].upper())
            self.fileWriter.WriteFile(
                baseRootPath + dirPath + ffffffff + '.c', content)



    def genUserFile(self):
        # TODO: do not change user code
        baseRootPath = 'Core/'

        # tools
        baseRootPath = '.vscode/'
        ffffffff = "c_cpp_properties.json"
        self.fileWriter.WriteFile(
                baseRootPath + ffffffff, Variable.F_VSCODE_C_PRIORITY_JSON%(self.BigName.upper(), self.BigName.upper(), "path to rv64"))

    def generate(self, perip_file: str, package_file: str):
        self.__perip_struct = None
        self.__package_struct = None
        with open(perip_file, 'r') as f:
            self.__perip_struct = json.loads(f.read())
        with open(package_file, 'r') as f:
            self.__package_struct = json.loads(f.read())

        if self.__package_struct == None or self.__perip_struct == None:
            print("file not open. maybe json file is invalid or file permission error")
            exit(1)
        # loads json OK.
        # check perip
        for i in self.__perip_struct["peripheral"]:
            keys = i.keys()
            if "name" not in keys or "reg" not in keys:
                print("peripheral format error")
                exit(1)
        self.__perip_struct = self.__perip_struct["peripheral"]

        # check pack and get bigname
        content = self.__package_struct
        keys = content.keys()
        if "version" not in keys:
            print("no version info in file")
            return
        version_child = content["version"]
        ver_pre = version_child["pre"]
        is64 = version_child["is64"]
        bitSolution = 32
        if is64 == True:
            bitSolution = 64
        ver_seri = version_child["major"]
        self.BigName = ver_pre + str(bitSolution) + ver_seri
        print("product line :", self.BigName)

        self.__product_struct = self.__package_struct["product"]
        self.product_names = []
        for i in self.__product_struct:
            keys = i.keys()
            need_keys = ['name', 'per_base', 'mem', 'per']
            for mk in need_keys:
                if mk not in keys:
                    print("productline key error")
                    exit(1)
            self.product_names.append(i['name'])

        self.genBaseLib()
        self.genHalLib()
        self.genUserFile()


if __name__ == '__main__':
    generator = fileGenerator("../temp_prj")
    generator.generate(sys.argv[1], sys.argv[2])
    # dev_package_decoder(sys.argv[1])

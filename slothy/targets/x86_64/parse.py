#!/usr/bin/env python3
import xml.etree.ElementTree as ET



def print_form(node):
    name = node.attrib["asm"]
    operands = []

    additional = ""
    for operandNode in node.iter("operand"):
        operandIdx = int(operandNode.attrib["idx"])
        if operandNode.attrib["type"] == "reg":
            w = int(operandNode.attrib["width"])
            operands.append({ 
                "width": w,
                "pattern_name": f"{operandIdx}R{w}",
            })
        if operandNode.attrib["type"] == "flags":
            additional += "use_flags = true"


    print(f"""class {name}(X86_64Instruction):
    pattern = "{name} <aR64>, <bR64>, <cR64>"
    inputs = ["bR64", "cR64"]
    outputs = ["aR64"]
    {additional}""")

def main():
    root = ET.parse("instructions.xml")
    extension = ["BASE"]
    instruction_name = ["ADC"]
    form = ["(R64, R64)"]

    for instrNode in root.iter("instruction"):
        # Future instruction set extensions
        if instrNode.attrib["extension"] in ["AMD_INVLPGB", "ICACHE_PREFETCH"]:
            continue
        if instrNode.attrib["isa-set"] in ["AVX10_2_RC_256"]:
            continue
        # Deprecated instruction set extensions
        if instrNode.attrib["extension"] in ["MPX"]:
            continue

        # skip over all instruction not wanted
        if instrNode.attrib["extension"] not in extension:
            continue

        asm = instrNode.attrib["asm"]

        # format is something like: ADC (R64, R64)
        f = instrNode.attrib["string"]

        # continue over all instructions not wanted
        if instruction_name[0] not in asm:
            continue

        if form[0] not in f:
            continue
        print_form(instrNode)
        # for arch in instrNode.iter("architecture"):
        #     arch_name = arch.attrib["name"]
        # first = True
        # for operandNode in instrNode.iter("operand"):
        #     operandIdx = int(operandNode.attrib["idx"])

        #     if operandNode.attrib.get("suppressed", "0") == "1":
        #         continue

        #     if not first and not operandNode.attrib.get("opmask", "") == "1":
        #         asm += ", "
        #     else:
        #         asm += " "
        #         first = False

        #     if operandNode.attrib["type"] == "reg":
        #         registers = operandNode.text.split(",")
        #         register = registers[min(operandIdx, len(registers) - 1)]
        #         if not operandNode.attrib.get("opmask", "") == "1":
        #             asm += register
        #         else:
        #             asm += "{" + register + "}"
        #             if instrNode.attrib.get("zeroing", "") == "1":
        #                 asm += "{z}"
        #     elif operandNode.attrib["type"] == "mem":
        #         memoryPrefix = operandNode.attrib.get("memory-prefix", "")
        #         if memoryPrefix:
        #             asm += memoryPrefix + " "

        #         if operandNode.attrib.get("VSIB", "0") != "0":
        #             asm += "[" + operandNode.attrib.get("VSIB") + "0]"
        #         elif operandNode.attrib.get("moffs", "0") != "0":
        #             asm += "[0x1111111111111111]"
        #         else:
        #             asm += "[RAX]"

        #         memorySuffix = operandNode.attrib.get("memory-suffix", "")
        #         if memorySuffix:
        #             asm += " " + memorySuffix
        #     elif operandNode.attrib["type"] == "agen":
        #         agen = instrNode.attrib["agen"]
        #         address = []

        #         if "R" in agen:
        #             address.append("RIP")
        #         if "B" in agen:
        #             address.append("RAX")
        #         if "IS" in agen:
        #             address.append("2*RBX")
        #         elif "I" in agen:
        #             address.append("1*RBX")
        #         if "D8" in agen:
        #             address.append("8")
        #         if "D32" in agen:
        #             address.append("128")

        #         asm += " [" + "+".join(address) + "]"
        #     elif operandNode.attrib["type"] == "imm":
        #         if instrNode.attrib.get("roundc", "") == "1":
        #             asm += "{rn-sae}, "
        #         elif instrNode.attrib.get("sae", "") == "1":
        #             asm += "{sae}, "
        #         width = int(operandNode.attrib["width"])
        #         if operandNode.text is not None:
        #             imm = operandNode.text
        #         else:
        #             imm = (1 << (width - 8)) + 1
        #         asm += str(imm)
        #     elif operandNode.attrib["type"] in ["absbr", "relbr"]:
        #         asm = "1: " + asm + "1b"

        # if not "sae" in asm:
        #     if instrNode.attrib.get("roundc", "") == "1":
        #         asm += ", {rn-sae}"
        #     elif instrNode.attrib.get("sae", "") == "1":
        #         asm += ", {sae}"

        # print(asm)


if __name__ == "__main__":
    main()

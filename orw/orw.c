#include<unistd.h>
#include<seccomp.h>
#include<sys/syscall.h>

char shellcode[1024];

int main()
{
  scmp_filter_ctx ctx;
  ctx = seccomp_init(SCMP_ACT_ALLOW); 
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(open), 0); 
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(rt_sigreturn), 0); 
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(sigreturn), 0);
  seccomp_load(ctx);
  gets(shellcode);
  ((void(*)())shellcode)();
  return 0;
}

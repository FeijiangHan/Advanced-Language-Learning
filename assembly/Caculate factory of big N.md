```assembly
datas segment


    buff      db 6, ?, 6 dup(?)    
    
    
    Factorial dw 1, 999 dup(0)          ;阶乘，初值为1
    TempF     dw 1000 dup(0)            ;临时阶乘  
    
    
    Divisor   dw 1000 dup(0)            ;除数
    Quotient  dw 1000 dup(0)            ;商
    Result    db 1000 dup(0)            ;阶乘结果的BCD码形式
    
    N    dw 0                        ;N的2进制形式     
    i    dw 1                        ;2进制Factorial的字数  
    j    dw 0                        ;十进制阶乘的位数
    a    dw 1, 10, 100, 1000, 10000  ;Buff中字符转为二进制N时用到 
    b    dw ? 
    
    msg1 db  "Please input N: $"
    msg2 db 0ah, 0dh, "Press any key to exit...$" 
    msg3 db 0ah, 0dh, "N!=$"    
datas ends

stacks segment
	;
stacks ends

codes segment
    assume cs: codes, ds: datas, ss: stacks, es: datas
start:
               mov ax, datas
               mov ds, ax
               mov es, ax
               
               Main:
               ; -------------自己想的----------
               call Input    ;输入N
               call Factor   ;计算N!
               
               ; ----------借鉴网络------------
               call Convert  ;将2进制Factorial转为非压缩BCD码Result
               call Output
               jmp  Final
;------------------------------------------------------------------------------
;输入字符型N，转为2进制
               
               Input:            
    
               lea  dx, msg1
               mov  ah, 9
               int  21h
    
               lea  dx, buff ;输入字符串
               mov  ah, 10
               int  21h            
                                   
               lea  di, a    ;将输入字符串转化为整数存入N
               mov  ch, 0
               mov  cl, buff+1
               mov  si, cx              
      L0:      mov  ah, 0
               mov  al, buff[si+1]
               sub  al, 30h
               dec  si
               mov  bx, [di]
               mul  bx
               add  N,  ax         
               add  di, 2
               loop L0
               
               ret

;输入字符型N，转为2进制
;------------------------------------------------------------------------------               
;计算N!
;思路：先把答案复制到一个临时空间，在临时空间里从低位到高位做乘积运算，高位需要加上地位dx的进位，得到乘完以后的答案在放回原空间，而且每次发生进位都需要更新i的值，即二进制答案的字数，此后的循环多进行一次 
               
               Factor:        
               
               mov  bx, 1
               mov  cx, N 
      L1:      push cx
               lea  di, TempF
               lea  si, Factorial
               mov  cx, i
      L2:      mov  ax, [si]
               mov  [di], ax
               mov  ax, 0
               mov  [si], ax
               add  si, 2
               add  di, 2
               loop L2
                              
               lea  di, TempF
               lea  si, Factorial
               mov  cx, i               
      L3:      mov  ax, [di]
               mov  dx, 0
               mul  bx    ;16位:DX(高位)和 AX(低位)
               add  [si], ax ; 低位放在【si】，可能产生进位
               adc  [si+2], dx  ; 高位注意进位加法
               add  si, 2
               add  di, 2
               loop L3
                     
                     
               cmp  dx, 0 ; 判断进位
               jz   N1
               add  i, 1               
      N1:      inc  bx
               pop  cx
               loop L1
               
               ret
 
        
;-----------------------------------------------------
;将2进制Factorial转为BCD码Result
                                     
               Convert:                                                   
               
               mov ax, i
               mov bx, 2
               mul bx
               sub ax, 2
               mov b, ax                              
            
       L11:    call setD       ;设置除数
               call div10      
               
               ; 目的： 把f的一位送到result
               call Save
               
               ;------------------------------
               call cmpQz      ;测试商是否为零
               cmp  ax, 0
               jz   N5  
               ;-----------------------------------
               
               
               call movQF      ;将商移入Factorial做下一步除法   
               
               
               call clQ        ;商清零      
               
               
               
               jmp  L11               
       N5:     
               
               ret          
       ;..........................................
      
               setD:
               
               lea di, Quotient
               mov cx, i
               mov ax, 0
       L10:    mov [di], ax
               add di, 2
               loop L10
               mov ax, 0a000h ;8421第一个非法值即为0a
               mov [di-2], ax
               
               ret
               
       ;..........................................
      
               Div10:               
               mov bx, 16
               mov ax, i
               mul bx
               sub ax, 3
       
               mov  cx, ax              
       L7:     push cx
               call CmpFD
               jb   N2 ;如果原值小于除数则不需要相减，直接下一步运算即可。
               
               ; 原值减去除数得到余数
               call SubFD
               stc     ;进位标志设1                         
               jmp  N3   
               
       N2:     clc    
       
       N3:     call QSHL  ;注意： 进位标志cf会影响循环左移和循环右移
               call DSHR
               pop cx
               loop L7 
               
               ret   
  
      ;..........................................  

               Save:  
                ;初始j=0，把f第一个元素送给r第一个位置
               ; 然后更新j=1
               lea si, Factorial
               lea di, Result
               mov ax, j
               add di, ax
               mov al, [si]
               mov [di], al
               
               lea di, j
               mov ax, 1
               add [di], ax
               
               ret
                      
       ;..........................................

               cmpQz:
               
               lea  si, Divisor
               mov  cx, i
       L15:    mov  ax, [si] 
               cmp  ax, 0
               jnz  N4 ;不相等
               add  si, 2
               loop L15
   
       N4:     ret ;不等0的话，返回时ax就不是0
       
       ;..........................................
       
               movQF:

               lea di, Factorial
               lea si, Divisor
               mov cx, i
       L9:     mov ax, [si]
               mov [di], ax
               add si, 2
               add di, 2
               loop L9  
               
               ret
               
       ;...........................................
                      
               clQ:
               
               lea di, Divisor
               mov cx, i
               mov ax, 0
       L12:    mov [di], ax
               add di, 2
               loop L12 
               
               ret
                      
       ;.......................................... 
                                  
               CmpFD: 
                               
               lea  di, Quotient
               lea  si, Factorial
               add  di, b
               add  si, b
               mov  cx, i
               std  ;相反功能指令是STD，将方向标志位DF置1，在字串操作中使SI或DI的地址指针自动递减，字串处理由后往前。目的就是从高位向低位比较
               repz cmpsw ; ZF=1时，重复执行后边的指令，每次执行CX-1
                          ; 影响标志位
                          ; 相等则不断重复比较，直到不相等或比较完毕
                          ; 目的是相等则继续比较
               ret
      ;..........................................   
      
      
      
               ; 执行完以后，Factorial里面就是余数了，因为原值减去了除数
               SubFD: 
                                                                
               lea  di, Factorial
               lea  si, Quotient              
               mov  cx, i
               clc
       L4:     mov  bx, [si]
               sbb  [di], bx
               inc  si
               inc  si
               inc  di
               inc  di
               loop L4
               
               ret
               
     ;..........................................
               
               QSHL:
               
               lea  si, Divisor                            
               mov  cx, i   
       L5:     rcl  word ptr[si], 1
               inc  si
               inc  si
               loop L5
               
               ret

      ;..........................................
               
               DSHR:
               
               lea  si, Quotient
               add  si, b
               mov  cx, i
               clc   
       L6:     rcr word ptr[si], 1
               dec si
               dec si             
               loop L6
               
               ret
                                                          
;将2进制Factorial转为BCD码Result             
;-------------------------------------------------------------------------
;输出!
              Output: 
              
              lea dx, msg3
              mov ah, 9
              int 21h 
                                                           
              lea di, Result
              mov cx, j
              add di, cx
              sub di, 1  
              
       L14:   mov dl, [di]
              cmp dl, 0
              jnz L13
              dec di
              loop L14
              
       L13:   mov dl, [di]
              add dl, 30h
              mov ah, 2
              int 21h
              dec di
              loop L13
              
              ret

;输出N!                                                                   
;------------------------------------------------------------------------------                        
               Final:
                                            
               lea dx, msg2
               mov ah, 9
               int 21h 
               
               mov ah, 1
               int 21h     
                  
               mov ah, 4ch
               int 21h
codes ends
    end start

```



整个问题没办法在网上搜到，但是思考实现，进行模块化以后，或许就可以借助前人的经验得到结果。

[参考0：二进制转换为BCD码存储](https://blog.csdn.net/weixin_39531582/article/details/109978434)

[参考1：BCD码的输出](https://blog.csdn.net/qq_44871112/article/details/109046451)

```
(8)、功能0AH
功能描述：从标准输入设备上读入一个字节字符串，遇到“回车键”结束输入
(输入的字符在标准的输出设备上有回显)。如果该输入操作被重定向，那么，
将无法判断文件是否已到文件尾
入口参数：AH＝0AH
DS:DX＝存放输入字符的起始地址
接受输入字符串缓冲区的定义说明：
　　1、第一个字节为缓冲区的最大容量，可认为是入口参数；
　　2、第二个字节为实际输入的字符数(不包括回车键)，可看作出口参数；
　　3、从第三个字节开始存放实际输入的字符串；
　　4、字符串以回车键结束，回车符是接受的最后一个字符；
　　5、若输入的字符数超过缓冲区的最大容量，则多出的部分被丢弃，系统并
发出响铃，直到输入“回车”键才结束输入。
例如：
　　BUFF　80, ?, 80 DUP(?)　　　;最多接受80个字符
出口参数：无
```

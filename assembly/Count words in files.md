```assembly
;****************************************************
;程序功能：读取文本文件并统计单词个数        
;****************************************************

;数据段定义
DATAS SEGMENT
	strFileName db 'text01.txt',0   ;文件名；注意保存在bin文件夹下
	;---------------两个失败提示，都以0结尾，输出
	strOpenFailed db 'the file open failed',07h,0  ;打开失败
	strReadFailed db 'the file read failed',07h,0  ;读取失败
	
	string1 db 'alpha: $';
	string2 db '$';
	
	;------------扩展功能：输出每个字母所占的比例-------
	string3 db ' frequency: $';
	string4 db '.$';输出比例时的小数点
	
	array db 26 dup (0) ;统计字母个数
	others db 0         ;其他字符个数
	buffer db ?         ;读取缓冲区
	EOF db 0001h        ;读到文件尾部返回EOF
	SumNums db 0        ;统计字符总个数

DATAS ENDS

STACKS SEGMENT
    ;此处输入堆栈段代码
STACKS ENDS

CODES SEGMENT
    ASSUME CS:CODES,DS:DATAS,SS:STACKS
START:
   mov AX,DATAS
   mov DS,AX
   
   
   
   mov DX,OFFSET strFileName  ;文件偏移地址
   mov ax,3dh                 ;打开文件
   int 21h
   ;成功cf=0；失败cf=1
   ;创建成功就跳转opensuccess
   jnc openSuccess
   
   ;调用错误处理统一函数并结束
   ;提前使si指向输出的内容
   mov si,offset strOpenFailed
   call Wrong ;打印si指向的错误内容
   jmp over
   
   
   
   ; 以下是创建成功的处理部分
   openSuccess:
     mov bx,ax       ; 保存文件句柄，用于读写关闭文件使用
 ;------------------------------------------------------------------------  
 ;-----------------这一块是主架构，循环读取单个字符，并对这个字符进行计数------
     againRead:
      ;--------功能1.读取字符的函数-------
     call ReadChar  
     ;------------读错误跳转---------
     ; -- 如果cf=0，代表文件读取成功
     ; -- cf=1，文件读取失败，跳转到错误处理
     jc ReadError    
     ;-----------读取完文件的跳转-----
     cmp al,EOF      
                     ; 关闭文件，输出结果（最后一步才会执行）
     jz charOk       ; mov ah,3eh的入口条件是bx保存的文件代号
     ;-----------功能2.统计个数的函数-----
     call Statistic   ;每一步都会执行
     jmp againRead    ;循环读文件，读取并统计字符 
;---------------------------------------------------------------------------




;文件读取失败
ReadError:
	 lea si,strReadFailed  ;调用Wrong函数之前的预处理
	 call Wrong
	
	
;****************************************************
; 打印失败函数（复用性强）
; 调用前需要提前赋值si的值
; 打印的字符串需要以0结尾
; 优化：loop+length
;****************************************************
Wrong proc
   Again:
   mov dl,[si]
   inc si
   or dl,dl ;目的是判断字符串结束
   jz L1 ;遇到0的时候就不再输出，直接退出函数
   mov ah,02h
   int 21h
   jmp Again ;循环输出字符串的字符
   L1:ret
Wrong endp



;文件读取结束，关闭文件，输出结果
charOk:
   mov ah,3eh  ; 3Eh,关闭文件；入口条件是bx保存的文件代号
   int 21h
  
   mov dl,0ah
   mov ah,02h
   int 21h
   call Show
   
;结束     
over:
   mov ah,07h
   int 21h
   mov ah,4ch
   int 21h 
   
   
   

;------------------------------------------------------------------   
;读取字符函数
;读取的字符在al里
;读取结束al为EOF
;读取失败cf=1，读取成功cf=0
ReadChar proc 
    mov cx,1 ;读取字符个数
    mov dx,offset buffer ;字符缓存
    
     ;------文件读取指令---------
     ;--DX:数据缓冲区逻辑首地址
     ;--BX:文件代号
     ;--CX:读取字节的个数
     ;cf=0读取成功，cf=1读取失败
     ;AX=实际读取的字节数
     mov ah,3fh
     int 21h
     ;-------------------------
     
    
    jc L1 ;跳转，cf=1 代表读取失败
    
    ;下面是读取成功的处理,Cf一定为0
    cmp ax,cx ;判断是否读取到文件尾部、或者文件本来就是空；如果读取字节数为0，则ax一定小于cf=1
    mov al,EOF ;先把读取的字符视为EOF
    jb L2 ;如果读取到文件尾部，AX = 0，直接返回
    mov al,buffer ;如果没读到文件尾部就覆盖EOF为真正被读取的字符
   
            ;cmp是进行的减操作,有进位或借位,CF=1
    L2: CLC ;读取成功时cf为0，但是还是要清空cf，确保cf一定为0
    L1: ret ;读取失败时不清空cf一定为1
    
ReadChar endp
;------------------------------------------------------------------   



;----------------------------计算出现次数----------------------------
;-- 先进行比较，有三种处理的情况
;-----------1. 处理大写字母
;-----------2. 处理小写字母
;-----------3. 处理非字母
;-- 然后进行计数，也对应了三种，但是把大写和小写字母统计到一起了
;-----------1. 计数大写字母
;-----------2. 计数小写字母
;-----------3. 计数非字母（ignore）

Statistic proc
    push dx  ;保存dx
    
    ; al已经从文件中读取了
    ; dl放需要显示的字符，用来输出
    mov dl,al
    mov ah,02h
    int 21h
    
    pop dx ; 恢复dx
    
    
    ; 对大写字母区域识别
    mov cl,41h    ;A
    ; info: array 存放26个字母的出现次数
    lea di,array  ; 大写字母计数区
    
    ;比较文件中读取的al和我们指定的A-Z
    mov ch,al
    cmp ch,cl      
    jb otherChars  ;不是字母的跳转
    cmp ch,5ah     ;Z
    ja lowerCase   ; 小写字母的跳转

;---------如果前面没跳转，代表处理的是大写字母--------
    capital:     ;大写字母处理
    cmp ch,cl    ;ch=读取的字符，cl=A；先从A开始比较
    je addChar   ;相等则跳转到字母加法程序，给对应字母个数加一
    
    ;如果在A之后，就继续增加，从A-Z都试一遍，直到找出合适的
    ;同步更新字母和个数数组的指针
    inc cl
    add di,1
    jmp capital ;loop again
    
    
;---------跳转，处理的是小写字母--------
    lowerCase:
     mov cl,61h   ;a
     lea di,array ; 小写字母计数区
     mov ch,al 
     cmp ch,cl
     jb otherChars
     cmp ch,7ah
     ja otherChars
     
    lower: ;小写字母处理
    cmp ch,cl
    je addChar  ; 跳转到字母加法程序

    inc cl
    add di,1
    jmp lower
;-------------------------------------

    ; 计数,大小写统一
    ; 清空ch；去除对应di位置的字母个数；加一；放回
    addChar:
    xor ch,ch
    mov ch,[di]
    inc ch
    mov [di],ch
    
    otherChars:
    inc others ;记录非字母个数

    ret
Statistic endp
;---------------------------统计个数部分结束--------------------------------




;-----------------------输出最后的结果--------------------------------
Show proc
   lea si,array
   mov di,41h
   
   Looping:
   ; 输出个数
   lea dx,string1
   mov ah,09h
   int 21h
   
   mov dx,di
   mov ah,02h
   int 21h
   
   mov dl,20h
   mov ah,02h
   int 21h

   xor ax,ax
   mov al,[si] ;把array里面的数据放到al里面，等等做除法输出
   call DisplayNum ;输出array数组
   
   ; 输出频率
   lea dx,string3
   mov ah,09h
   int 21h

   ;
   ;xor ax,ax
   ;mov al,[si] ;把array里面的数据放到al里面，等等做除法输出
   inc si
   
   ;call DisPlayFrequency
   call EndLine ;输出空格
   
   inc di
   cmp di,5bh
   jb Looping
   
   
   mov ah,4ch
   int 21h
   ret
Show endp
    

;-----------------------输出字母频率个数--------------------
;----notice: 每个字母出现的次数需要在100以内
DisplayNum proc near
mov bl,10
div bl
;除法后结果放在ax里
push ax
;输出al（低位是商）
mov dl,al
add dl,30h
mov ah,02h
int 21h
pop ax

;输出ah
mov dl,ah
add dl,30h
mov ah,02h
int 21h

mov dl,20h
mov ah,02h
int 21h
ret
DisplayNum endp



;-------------------输出空格-----------------
EndLine proc near
   mov dl,20h
   mov ah,02h
   int 21h
   
   mov dl,20h
   mov ah,02h
   int 21h
   
   mov dl,20h
   mov ah,02h
   int 21h
   
   mov dl,20h
   mov ah,02h
   int 21h
   
   ret
EndLine endp


   
   
;--------------------开发中：统计频率---------------------------
DisPlayFrequency proc near
;计算字符总数
push si
push di
push ax
push cx

mov cx,26
lea si,array
xor bl,bl

CacuSum:
add bl,[si]
inc si
loop CacuSUm
pop cx
pop ax
pop di
pop si

div bl

;除法后结果放在ax里
push ax
;输出al
mov dl,al
add dl,30h
mov ah,02h
int 21h
pop ax


;输出小数点
push ax
push dx
lea dx,string4
mov ah,09h
int 21h
pop dx
pop ax


;输出ah
mov dl,ah
add dl,30h
mov ah,02h
int 21h

mov dl,20h
mov ah,02h
int 21h
ret
DisPlayFrequency endp


dev_func proc near

  mov ax,bx
  mov dx,0
  div cx
  mov bx,dx
  mov dl,al
  add dl,30h
  mov ah,2h
  int 21h
  ret

dev_func endp
;--------------------------------------------------------------------------


CODES ENDS
    END START
```


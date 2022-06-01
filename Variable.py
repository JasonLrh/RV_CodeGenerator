
'''
----------------- tools ------------------
.vscode
    c_cpp_properties.json
--------------- user file ----------------
.gitignore
Makefile
BootConf
    riscv_flash.ld
    startup_riscv.s
Core
    Inc
        main.h ...
        {pName}_hal_conf.h
    Src
        main.c
--------------- lib file -----------------
Drivers
    BaseLib
        Include
            general_system.h
        Device
            Include
                {pName}xx.h
                {pName}{vName}.h
        BSP
    {pName}_HAL_Driver
        Inc
            {pName}_hal_def.h
            {pName}_hal_[per].h
            {pName}_hal.h
        Src
            {pName}_hal_[per].c
            {pName}_hal.c
'''

LISENCE = '''\
/**
  ******************************************************************************
  * author : jasonlrh
  * email  : 534459497@qq.com
  ******************************************************************************
  */
'''

F_GENERAL_SYSTEM_H = '''\
#include <stdint.h>


#ifdef __cplusplus
  #define   __I     volatile             /*!< Defines 'read only' permissions */
#else
  #define   __I     volatile const       /*!< Defines 'read only' permissions */
#endif
#define     __O     volatile             /*!< Defines 'write only' permissions */
#define     __IO    volatile             /*!< Defines 'read / write' permissions */

/* following defines should be used for structure members */
#define     __IM     volatile const      /*! Defines 'read only' structure member permissions */
#define     __OM     volatile            /*! Defines 'write only' structure member permissions */
#define     __IOM    volatile            /*! Defines 'read / write' structure member permissions */

#ifndef   __ASM
  #define __ASM                                  __asm
#endif
#ifndef   __INLINE
  #define __INLINE                               inline
#endif
#ifndef   __STATIC_INLINE
  #define __STATIC_INLINE                        static inline
#endif
#ifndef   __STATIC_FORCEINLINE                 
  #define __STATIC_FORCEINLINE                   __attribute__((always_inline)) static inline
#endif                                           
#ifndef   __NO_RETURN
  #define __NO_RETURN                            __attribute__((__noreturn__))
#endif
#ifndef   __USED
  #define __USED                                 __attribute__((used))
#endif
#ifndef   __WEAK
  #define __WEAK                                 __attribute__((weak))
#endif
#ifndef   __PACKED
  #define __PACKED                               __attribute__((packed, aligned(1)))
#endif
#ifndef   __PACKED_STRUCT
  #define __PACKED_STRUCT                        struct __attribute__((packed, aligned(1)))
#endif
#ifndef   __PACKED_UNION
  #define __PACKED_UNION                         union __attribute__((packed, aligned(1)))
#endif
'''

F_HAL_DEF_H = '''\
    #include "rv32f0xx.h"

typedef enum
{
  HAL_OK       = 0x00,
  HAL_ERROR    = 0x01,
  HAL_BUSY     = 0x02,
  HAL_TIMEOUT  = 0x03
} HAL_StatusTypeDef;

typedef enum
{
  HAL_UNLOCKED = 0x00,
  HAL_LOCKED   = 0x01
} HAL_LockTypeDef;

#define HAL_MAX_DELAY      0xFFFFFFFFU

#define HAL_IS_BIT_SET(REG, BIT)         (((REG) & (BIT)) == (BIT))
#define HAL_IS_BIT_CLR(REG, BIT)         (((REG) & (BIT)) == 0U)

#define __HAL_LINKDMA(__HANDLE__, __PPP_DMA_FIELD__, __DMA_HANDLE__)               \
                        do{                                                      \
                              (__HANDLE__)->__PPP_DMA_FIELD__ = &(__DMA_HANDLE__); \
                              (__DMA_HANDLE__).Parent = (__HANDLE__);             \
                          } while(0)

#define UNUSED(x) ((void)(x))
#define __HAL_RESET_HANDLE_STATE(__HANDLE__) ((__HANDLE__)->State = 0)

#if (USE_RTOS == 1)
  #error " USE_RTOS should be 0 in the current HAL release "
#else
  #define __HAL_LOCK(__HANDLE__)                                           \
                                do{                                        \
                                    if((__HANDLE__)->Lock == HAL_LOCKED)   \
                                    {                                      \
                                       return HAL_BUSY;                    \
                                    }                                      \
                                    else                                   \
                                    {                                      \
                                       (__HANDLE__)->Lock = HAL_LOCKED;    \
                                    }                                      \
                                  }while (0)

  #define __HAL_UNLOCK(__HANDLE__)                                          \
                                  do{                                       \
                                      (__HANDLE__)->Lock = HAL_UNLOCKED;    \
                                    }while (0)
#endif /* USE_RTOS */

#define __weak   __attribute__((weak))
#define __ALIGN_END    __attribute__ ((aligned (4)))
#define ALIGN_32BYTES(buf)  buf __attribute__ ((aligned (32))) 
#define __RAM_FUNC __attribute__((section(".RamFunc")))
#define __NOINLINE __attribute__ ( (noinline) )

#ifdef __cplusplus
}
#endif
'''

F_VSCODE_C_PRIORITY_JSON = '''\
{
    "configurations": [
        {
            "name": "Linux",
            "includePath": [
                "Drivers/BaseLib/Include",
                "Drivers/BaseLib/Device/Include",
                "Drivers/%s_HAL_Driver/Inc",
                "Core/Inc"
            ],
            "defines": [
                "%s"
            ],
            "compilerPath": "%s",
            "cStandard": "gnu17",
            "cppStandard": "gnu++14",
            "intelliSenseMode": "gcc-arm"
        }
    ],
    "version": 4
}
'''

def getHAL_per_h(perName:str) -> str:
    perName = perName.upper()
    ret = '''\
#include "rv32f0xx_hal_def.h"

typedef enum {
  HAL_%s_STATE_RESET             = 0x00U,
  HAL_%s_STATE_READY             = 0x01U,
  HAL_%s_STATE_BUSY              = 0x02U,
  HAL_%s_STATE_TIMEOUT           = 0x03U,
  HAL_%s_STATE_ERROR             = 0x04U
} HAL_%s_StateTypeDef;

'''%(perName,perName,perName,perName,perName,perName) + '''\
typedef struct __%s_HandleTypeDef {
  %s_TypeDef               *Instance; 
  HAL_LockTypeDef          Lock; 
  __IO HAL_%s_StateTypeDef State;
  void (*handleInterrupt)(struct __%s_HandleTypeDef * h%s);
} %s_HandleTypeDef;
'''%(perName,perName,perName,perName,perName.lower(),perName)
    return ret


# F_HAL_PER_H = '''\
# #include "rv32f0xx_hal_def.h"

# typedef enum
# {
#   HAL_%s_STATE_RESET             = 0x00U,
#   HAL_%s_STATE_READY             = 0x01U,
#   HAL_%s_STATE_BUSY              = 0x02U,
#   HAL_%s_STATE_TIMEOUT           = 0x03U,
#   HAL_%s_STATE_ERROR             = 0x04U
# } HAL_%s_StateTypeDef;
# '''
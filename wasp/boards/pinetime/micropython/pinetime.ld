/* GNU linker script for the PineTime (nRF52832, 512K flash, 64K RAM) */

_flash_size = 512K;
_ram_size   = 64K;

/* The wasp-bootloader lives at 0x78000..0x80000 */
_bootloader_tail_size = 0x8000;

/* No internal filesystem and no ROMFS: wasp-os uses the external SPI NOR */
_fs_size = 0;
_micropy_hw_romfs_part0_size = 0;

/* produce a link error if there is not this amount of RAM for these sections */
_stack_size = 8K;
_minimum_heap_size = 32K;

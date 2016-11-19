set lines 190 
set pages 1000 
col dgname for a25 
col sector for 9999 
col blk for 99999 
col au for  999999999 
col hot_mb  for 99999999 
col cold_mb for 99999999 
col total_mb for 99999999 
col used_mb  for 99999999 
col req_mrr_fre_mb for 9999999 
col compat for a12 
col db_compat for a12 
Select group_number||':'||name DGname,  
       sector_Size sector, 
       block_size  blk, 
       allocation_unit_size AU, 
       State, 
       Type, 
       Total_MB, 
       FREE_MB, 
       HOT_USED_MB Hot_mb, 
       cold_used_mb cold_mb, 
       required_mirror_Free_mb Req_mrr_fre_mb, 
       usable_file_mb, 
        offline_disks  off_disk, 
        compatibility compat, 
        database_compatibility db_compat, 
        voting_files 
from v$asm_diskgroup 
/ 


      

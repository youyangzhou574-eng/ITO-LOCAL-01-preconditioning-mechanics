$ErrorActionPreference='Stop'
$taskRoot=$PSScriptRoot
$utf8=[System.Text.UTF8Encoding]::new($false)
function Write-OnceJson($name,$value) {
 $p=Join-Path $taskRoot $name
 $s=$value|ConvertTo-Json -Depth 30
 $bytes=$utf8.GetBytes($s+"`n")
 $f=[IO.File]::Open($p,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try {$f.Write($bytes,0,$bytes.Length)} finally {$f.Dispose()}
}
function Hash($p) {(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
$source=Join-Path $taskRoot 'compare_r2_r1_csv_only_recovery01.py'
$admissionPath=Join-Path $taskRoot 'R2_CSV_COMPARISON_RECOVERY01_SOURCE_ADMISSION.json'
$admission=Get-Content -LiteralPath $admissionPath -Raw|ConvertFrom-Json
if($admission.status -ne 'CSV_ONLY_RECOVERY01_SOURCE_ADMISSION_PASS' -or (Hash $source) -ne $admission.source_hashes.source){throw 'Source admission mismatch'}
$budgetPath=Join-Path $taskRoot 'BUDGET_LEDGER.json'
$budget=Get-Content -LiteralPath $budgetPath -Raw|ConvertFrom-Json
if($budget.local_csv_comparison_recovery.technical_recovery_used -ne 0 -or $budget.local_csv_comparison_recovery.technical_recovery_max -ne 1){throw 'Recovery budget already used'}
if([DateTimeOffset]::UtcNow -ge [DateTimeOffset]::Parse('2026-10-02T11:42:38.303801Z')){throw 'Window expired'}
$queue=Get-Content -LiteralPath (Join-Path $taskRoot 'R2_PRO_FOLLOWUP_QUEUE.json') -Raw|ConvertFrom-Json
if($queue.submission_pause_active){throw 'New pause active'}
$mem=Get-CimInstance Win32_OperatingSystem
$free=(Get-PSDrive E).Free
if($free -lt 23622320128){throw 'Insufficient E derived allowance plus margin'}
$reservation=[ordered]@{utc=[DateTimeOffset]::UtcNow.ToString('o');stage='ONE_AUTHORIZED_EXISTING_LOCAL_CSV_COMPARISON_RECOVERY';source_admission_sha256=(Hash $admissionPath);source_sha256=(Hash $source);controller_sha256=(Hash $PSCommandPath);free_E_bytes=$free;available_memory_bytes=[int64]$mem.FreePhysicalMemory*1024;entry_calls_max=1;ODB_calls=0;NPZ_reads=0;science_reruns=0;solver_calls=0;extraction_calls=0;transport_calls=0;next_check_automation='ito-r2-pro';next_check_minutes=5;automatic_retry_allowed=$false}
Write-OnceJson 'R2_CSV_COMPARISON_RECOVERY01_EXEC_RESERVATION.json' $reservation
$budget.local_csv_comparison_recovery.technical_recovery_used=1
$budget.status='LOCAL_CSV_COMPARISON_RECOVERY01_RESERVED'
$budget.attempt_events+= [pscustomobject]@{event='LOCAL_CSV_COMPARISON_RECOVERY01_RESERVED';utc=$reservation.utc;normal_failed_intent_retained=$true;native_budget_delta=0;ODB_budget_delta=0;recovery_budget_delta=1}
[IO.File]::WriteAllText($budgetPath,($budget|ConvertTo-Json -Depth 30),$utf8)
Write-OnceJson 'R2_CSV_COMPARISON_RECOVERY01_ENTRY_LAUNCH.json' ([ordered]@{utc=[DateTimeOffset]::UtcNow.ToString('o');controller_PID=$PID;entry=$source;argument='--run';entry_calls=1;next_check_automation='ito-r2-pro';next_check_minutes=5;automatic_retry_allowed=$false})
$stdout=Join-Path $taskRoot 'R2_CSV_COMPARISON_RECOVERY01_STDOUT.log'
$stderr=Join-Path $taskRoot 'R2_CSV_COMPARISON_RECOVERY01_STDERR.log'
$entryExit=$null
try {
 & 'C:\Users\yang\AppData\Local\Programs\Python\Python313\python.exe' $source --run 1> $stdout 2> $stderr
 $entryExit=$LASTEXITCODE
 if($entryExit -ne 0){throw ('CSV-only recovery exited '+$entryExit)}
} catch {
 Write-OnceJson 'R2_CSV_COMPARISON_RECOVERY01_FIRSTERROR_RECEIPT.json' ([ordered]@{utc=[DateTimeOffset]::UtcNow.ToString('o');error=$_.ToString();entry_exit=$entryExit;automatic_retry_allowed=$false;next_check_automation='ito-r2-pro';next_check_minutes=5;recovery_budget_exhausted=$true})
 throw
} finally {
 Write-OnceJson 'R2_CSV_COMPARISON_RECOVERY01_EXEC_EXIT.json' ([ordered]@{utc=[DateTimeOffset]::UtcNow.ToString('o');exit_code=$entryExit;entry_exit=$entryExit;stdout_sha256=$(if(Test-Path -LiteralPath $stdout){Hash $stdout}else{$null});stderr_sha256=$(if(Test-Path -LiteralPath $stderr){Hash $stderr}else{$null});ODB_calls=0;NPZ_reads=0;science_reruns=0;actual_entry_calls=1;automatic_retry_allowed=$false})
}
Get-Content -LiteralPath $stdout -Raw

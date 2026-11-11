Write-Host "Running maliphors-inator Tests" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host ""

$testFiles = @(
    "test_maliphors_inator_logic.py",
    "test_maliphors_inator_ui.py",
    "test_logging.py"
)

$failed = 0

foreach ($file in $testFiles) {
    Write-Host "Running tests in $file..." -ForegroundColor Cyan
    python -u $file *>&1 | Tee-Object -Variable output
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAILED] Tests in $file failed" -ForegroundColor Red
        $failed++
    } else {
        Write-Host "[PASSED] Tests in $file passed" -ForegroundColor Green
    }
    Write-Host "-" * 40
}

Write-Host ""
if ($failed -eq 0) {
    Write-Host "All test suites passed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "$failed test suite(s) failed!" -ForegroundColor Red
    exit 1
}
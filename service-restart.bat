@echo off
title SidGifari-dns-resolver

echo
SidGifari-dns-resolver.exe -service stop
ipconfig /flushdns
SidGifari-dns-resolver.exe -service start
echo.
:end
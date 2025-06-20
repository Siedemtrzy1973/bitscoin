/*
 * Projekt BitsCoin 2025
 * Autorzy: Grupa Siedemtrzy
 * Fork Bitcoin Core – niezależna sieć BitsCoin
 * © 2025 Grupa Siedemtrzy. Wszelkie prawa zastrzeżone.
 */

// Copyright (c) 2023 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <kernel/cs_main.h>
#include <sync.h>

RecursiveMutex cs_main;

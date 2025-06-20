/*
 * Projekt BitsCoin 2025
 * Autorzy: Grupa Siedemtrzy
 * Fork Bitcoin Core – niezależna sieć BitsCoin
 * © 2025 Grupa Siedemtrzy. Wszelkie prawa zastrzeżone.
 */

// Copyright (c) 2022 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <bench/bench.h>
#include <bench/data.h>
#include <util/strencodings.h>

static void HexStrBench(benchmark::Bench& bench)
{
    auto const& data = benchmark::data::block413567;
    bench.batch(data.size()).unit("byte").run([&] {
        auto hex = HexStr(data);
        ankerl::nanobench::doNotOptimizeAway(hex);
    });
}

BENCHMARK(HexStrBench, benchmark::PriorityLevel::HIGH);

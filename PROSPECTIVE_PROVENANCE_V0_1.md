# Prospective analysis provenance v0.1

The standalone repository was imported after the analyses were developed. Prospectivity therefore cannot be judged from the `frogcs` commit timestamps alone. The development history is preserved in `zuizui0223/284b`, PR #66, where contract-freeze, implementation and run commits are ordered explicitly.

## NAAMP primary

- protocol freeze: `e41113d68d2d945cfac74560f49372cb8107adfb` — 2026-09-24 15:04:50 UTC
- model freeze: `1d04c8c837f90c39997acae5c74912750e65b8f3` — 15:10:55
- implementation: `17420ef3aa0e250bb61d677b429a1f5a23464379` — 15:11:04
- run: `23eeaa6e0111848170fe5e332aabba509c37820b` — 15:11:07
- result receipt freeze: `bee819d06263142c99c723500965435fac297bc6` — 15:13:14

## NAAMP secondary / network / robustness

- secondary endpoints freeze: `de881f059dcedfafed9068a406235e642afe78c1` — 22:11:50
- secondary implementation: `5a51a9e5e20a17cc0897572e4e29fbcf251755ad` — 22:11:58
- secondary run: `5e3b9b4954bb9df44f7743647abddaa3966c0840` — 22:12:03
- network H4 freeze: `d448f7e8577aeb1f12f035cb8fe7408448397bb4` — 22:17:51
- network run: `946c774477d854d5c257375dcd93df26230dd470` — 22:17:57
- joint-weather/DOY robustness freeze: `2131191ee2835fd30a8e5066fca620bbd6ae5d15` — 22:20:45
- joint-weather run: `579efacd22a12006b2310e14f674626e5e079a29` — 22:20:50
- activation/conditional-overlap contract freeze: `5a6a06fb3af7de29455ff0e39a8ceee9c3f81cd0` — 22:27:43
- activation/conditional-overlap run: `be768ae8f45c535840537898a8cda7871e1af0fa` — 22:27:50

## FrogID validation

The FrogID path contains several transport/schema repairs before weather values were opened. The relevant scientific contract and final transport were frozen before the successful external validation.

- external validation gate freeze: `dc30cc22de97da9414b2acbdcbdaf385d7ca5739` — 22:45:17
- weather-link sample freeze: `103cc935ef1c71dc34f4204ffc0a14322008d9d7` — 22:51:16
- rain validation freeze: `559d980dcf3ffc0a214e993ea3314f00f4792c0e` — 22:54:37
- final ERA5 transport freeze: `830d898fdf74b0b31e1450f818f1df13e6f5d4aa` — 2026-09-25 00:30:22
- final implementation: `d6bf0b78a8048dd6ffe321876dd67947e45d7995` — 00:31:52
- run: `8bc4e8de81bd31a433c9ca2ac1d6e379ed896ffc` — 00:31:55
- successful result freeze: `df4cfb269f341879fcace26beab8fd7f84e4cc9e` — 00:41:50

## Manuscript wording rule

Use:

> Analysis contracts were frozen in the development repository before the corresponding effect estimation; commit provenance is preserved in the standalone reproducibility record.

Avoid implying that the standalone `frogcs` import timestamp itself demonstrates prospectivity.

## Boundary

Later repairs that occur after an effect was opened are labelled explicitly as post-opening specification, transport or serialization repairs and cannot be upgraded to confirmatory evidence.

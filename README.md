---
title: Flow past a cylinder and Parareal
author: Johan Hidding and Pablo Rodríguez
---

Aim: simulate the turbulent flow past a cylinder in OpenFOAM and parallelise with Parareal.

Steps:

1. Follow the [tutorial](https://wiki.openfoam.com/Vortex_shedding_by_Joel_Guerrero_2D) at [Wolf Dynamics](http://www.wolfdynamics.com/wiki/T5_2D_cylinder.pdf), supplementary material: [vortex_shedding.tar.gz](http://www.wolfdynamics.com/wiki/vortex_shedding.tar.gz).
2. Run tutorial straight from Python using pyFOAM.
3. Run parallel-in-time using Parareal in Python with Noodles.

# Problem

![Flow around cylinder with Reynold's number 200.](./img/case-result.png)

To install the requirements, also clone [ParaNoodles](https://github.com/ParallelWindfarms/paranoodles) and run `pip install .` from its project root. To install additional requirements, have OpenFOAM installed and:

```shell
pip install -r requirements.txt
```

If you use Python [poetry](https://python-poetry.org/), use this instead:

```shell
poetry install
```

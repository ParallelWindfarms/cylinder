# Adios specifics
To enable Adios output on a case,

``` {.c file=system/controlDict}
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  6                                     |
|   \\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}

<<control-dict>>

functions {
    <<control-functions>>
}
```

Set the application to `icoFoam`.

``` {.c #control-dict}
application     icoFoam;
```

We'd like the simulation to run from the `latestTime` until the specified `endTime`, so we get restart functionality. In fact, we can copy the skeleton and one time-frame of data to continue the simulation.

``` {.c #control-dict}
startFrom       latestTime;
stopAt          endTime;
```

The rest of the top-level paramaters remain unchanged.

``` {.c #control-dict}
startTime       0;
endTime         350;
deltaT          0.05;
writeControl    runTime;
writeInterval   1;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
```

To enable Adios we need to include it in the `functions` section of the `controlDict`.

``` {.c #control-functions}
#include "adiosWrite"
```

The rest of the `functions` section remains the same.

``` {.c .bootstrap-fold #control-functions}
inMassFlow
{
    type            surfaceFieldValue;

    libs ("libfieldFunctionObjects.so");
    enabled         true;

//        writeControl     outputTime;
writeControl   timeStep;
writeInterval  1;

    log             true;

    writeFields     false;

    regionType          patch;
    name      in;

operation       sum;
    fields
    (
        phi
    );
}

outMassFlow
{
    type            surfaceFieldValue;

    libs ("libfieldFunctionObjects.so");
    enabled         true;

//writeControl     outputTime;

writeControl   timeStep;
writeInterval  1;

    log             yes;

    writeFields     false;

//writeFields     true;
//surfaceFormat   raw;

    regionType          patch;
    name      out;

operation       sum;
    fields
    (
        phi
    );
}

fieldAverage
{
    type            fieldAverage;
    libs ("libfieldFunctionObjects.so");
    enabled         true;
    writeControl   outputTime;

//writeControl   timeStep;
//writeInterval  100;

//cleanRestart true;

//timeStart       20;
//timeEnd         200;

    fields
    (
        U
        {
            mean        on;
            prime2Mean  on;
            base        time;
        }

        p
        {
            mean        on;
            prime2Mean  on;
            base        time;
        }
    );
}

///////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////

forces_object
{
type forces;
libs ("libforces.so");

//writeControl outputTime;
writeControl   timeStep;
writeInterval  1;

//// Patches to sample
//patches ("body1" "body2" "body3");
patches ("cylinder");

//// Name of fields
pName p;
Uname U;

//// Density
rho rhoInf;
rhoInf 1.;

//// Centre of rotation
CofR (0 0 0);
}

///////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////

forceCoeffs_object
{
// rhoInf - reference density
// CofR - Centre of rotation
// dragDir - Direction of drag coefficient
// liftDir - Direction of lift coefficient
// pitchAxis - Pitching moment axis
// magUinf - free stream velocity magnitude
// lRef - reference length
// Aref - reference area
type forceCoeffs;
libs ("libforces.so");
//patches ("body1" "body2" "body3");
patches (cylinder);

pName p;
Uname U;
rho rhoInf;
rhoInf 1.0;

//// Dump to file
log true;

CofR (0.0 0 0);
liftDir (0 1 0);
dragDir (1 0 0);
pitchAxis (0 0 1);
magUInf 1.0;
lRef 1.0;         // reference lenght for moments!!!
Aref 2.0;         // reference area 1 for 2d

    writeControl   timeStep;
    writeInterval  1;
}

///////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////

minmaxdomain
{
type fieldMinMax;
//type banana;

libs ("libfieldFunctionObjects.so");

enabled true;

mode component;

writeControl timeStep;
writeInterval 1;

log true;

fields (p U);
}
```


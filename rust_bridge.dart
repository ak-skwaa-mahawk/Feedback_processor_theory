typedef PiRTwoSolitonFunc = Double Function(Double, Double, Bool);
typedef PiRTwoSoliton = double Function(double, double, bool);

static final PiRTwoSoliton _twoSoliton = _nativeLib
    .lookup<NativeFunction<PiRTwoSolitonFunc>>("pi_r_two_soliton_pulse")
    .asFunction();

static double computeTwoSolitonPulse(double k1, double k2, bool orderMatters) =>
    _twoSoliton(k1, k2, orderMatters);
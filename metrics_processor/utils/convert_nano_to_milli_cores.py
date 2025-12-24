def convert_nano_to_milli_cores(nano_cores):
    if isinstance(nano_cores, str):
        # Remove 'n' suffix if present and convert to int
        _cpuNanocores = int(nano_cores.rstrip('n'))
    else:
        _cpuNanocores = int(nano_cores)
    
    _cpuUsageMillicores = _cpuNanocores / 1_000_000

    return _cpuUsageMillicores
def convert_ki_to_mi(ki_bytes):
    if isinstance(ki_bytes, str):
        # Remove 'Ki' suffix if present and convert to int
        _memoryKibibytes = int(ki_bytes.rstrip('Ki'))
    else:
        _memoryKibibytes = int(ki_bytes)
    
    # Convert Kibibytes to Mebibytes (1 Mi = 1024 Ki)
    _memoryMebibytes = _memoryKibibytes / 1024

    return _memoryMebibytes


# Features
- Device Discovery: Automatically detects all active devices on your network
- Comprehensive Information: Retrieves IP addresses, device names (when available), and MAC addresses
- Multiple Scanning Modes:
    - Ping Mode: Quick network discovery showing active/inactive devices
    - Full Scan Mode: Detailed analysis with device identification
- Multi-Interface Support: Works with both wireless (Wi-Fi) and Ethernet connections
- Bilingual Support: Compatible with Spanish and English Windows systems
- Threaded Operations: Fast parallel scanning for efficient network discovery
- Color-Coded Output: Easy-to-read results with color highlighting
- Graceful Exit: Proper handling of interruptions (Ctrl+C)

# Requirements
```pip install colorama```

# Usage
Basic scan (default: Spanish, Ethernet)

```python main.py```

Wireless interface scan in English

```python main.py -L en -I wireless```

Quick ping discovery mode

```python main.py -L es -I ethernet -m ping```

Full scan with wireless interface

```python main.py -L en -I wireless -m default ```

# Command Line Options
-L, --language: System language (es for Spanish, en for English)
-I, --interface: Network interface (wireless or ethernet)
-m, --mode: Scan mode (ping for discovery, default for full scan)
-?, -h: Show help and usage information

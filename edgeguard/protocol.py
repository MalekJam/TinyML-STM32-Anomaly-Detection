"""UART protocol: S,ms,ax,ay,az,gx,gy,gz or R,ms,mode,score_u6,limit_u6,A|N."""

def parse_line(text):
    parts = text.strip().split(",")
    if parts[0] == "S" and len(parts) == 8:
        try:
            return {"kind": "sample", "t_ms": int(parts[1]),
                    **dict(zip(("ax", "ay", "az", "gx", "gy", "gz"), map(int, parts[2:])))}
        except ValueError:
            return None
    if parts[0] == "R" and len(parts) == 6:
        try:
            mode, alert = parts[2], parts[5]
            if mode not in ("HEURISTIC", "TINYML") or alert not in ("A", "N"):
                return None
            return {"kind": "result", "t_ms": int(parts[1]), "mode": mode,
                    "score": int(parts[3])/1e6, "threshold": int(parts[4])/1e6,
                    "anomaly": alert == "A"}
        except ValueError:
            return None
    if parts[0] in ("BOOT", "READY", "ERROR"):
        return {"kind": "status", "message": text.strip()}
    return None

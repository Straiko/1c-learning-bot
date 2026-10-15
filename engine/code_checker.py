import re
import difflib
from typing import List, Tuple, Dict, Any, Optional

def tokenize(s: str) -> List[str]:
    # Strip comments
    s = re.sub(r'//.*$', '', s).strip()
    if not s:
        return []
    # Tokenize strings, identifiers/keywords/numbers, and symbols
    pattern = r'\"[^\"]*\"|[a-zA-Zа-яА-ЯёЁ_0-9]+|[^\s\w]'
    raw_tokens = re.findall(pattern, s)
    normalized = []
    for t in raw_tokens:
        if t.startswith('"') and t.endswith('"'):
            normalized.append(t)
        else:
            normalized.append(t.lower())
    while normalized and normalized[-1] == ';':
        normalized.pop()
    return normalized

def clean_statements(text: str) -> List[Tuple[str, str, Tuple[str, ...]]]:
    statements = []
    for line in text.strip().splitlines():
        line_clean = re.sub(r'//.*$', '', line).strip()
        if line_clean:
            toks = tokenize(line_clean)
            if toks:
                statements.append((line.strip(), line_clean, tuple(toks)))
    return statements

def get_env_for_statement(toks: Tuple[str, ...], default_env: str, current_env: str) -> str:
    if toks and toks[0] == "&наклиенте":
        return "&НаКлиенте"
    if toks and toks[0] == "&насервере":
        return "&НаСервере"
    return current_env or default_env

def diagnose_mismatch(user_raw: str, exp_raw: str, u_tokens: List[str], e_tokens: List[str]) -> str:
    # Check directive
    if e_tokens and e_tokens[0] in ("&наклиенте", "&насервере"):
        if not u_tokens or u_tokens[0] != e_tokens[0]:
            return f"Забыта директива контекста: на скриншоте указано <code>{exp_raw}</code>"

    # Specific method name checks from the screenshot
    if "прочитатьзначениеjson" in e_tokens and "прочитатьjson" in u_tokens:
        return "На скриншоте используется именно <code>ПрочитатьЗначениеJSON</code>, а вы написали <code>ПрочитатьJSON</code>"

    # Compare token by token
    for u, e in zip(u_tokens, e_tokens):
        if u != e:
            if u.startswith('"') and e.startswith('"'):
                return f"Не совпадает текст в кавычках: вы написали <code>{u}</code>, а на скриншоте <code>{e}</code>"
            return f"Несовпадение: вы написали <code>{u}</code>, а на скриншоте <code>{e}</code>"

    if len(u_tokens) < len(e_tokens):
        missing = " ".join(e_tokens[len(u_tokens):])
        return f"В строке не хватает: <code>{missing}</code>"
    if len(u_tokens) > len(e_tokens):
        extra = " ".join(u_tokens[len(e_tokens):])
        return f"Лишние операторы или слова в конце: <code>{extra}</code>"

    return "Синтаксис строки отличается от кода на скриншоте"

def check_code_submission(user_code: str, expected_code: str, env_name: str, env_desc: str) -> Dict[str, Any]:
    exp_stmts = clean_statements(expected_code)
    user_stmts = clean_statements(user_code)

    # Precompute environment per expected statement
    exp_envs = []
    curr = "&НаКлиенте" if env_name.startswith("&НаКлиенте") else "&НаСервере"
    for _, _, toks in exp_stmts:
        if toks and toks[0] == "&наклиенте":
            curr = "&НаКлиенте"
        elif toks and toks[0] == "&насервере":
            curr = "&НаСервере"
        exp_envs.append(curr)

    if not user_stmts:
        return {
            "is_correct": False,
            "accuracy": 0.0,
            "matched_count": 0,
            "total_expected": len(exp_stmts),
            "errors": [{
                "type": "empty",
                "env": curr,
                "message": "Вы не ввели код! Пожалуйста, отправьте текст программы.",
                "user_line": "",
                "expected_line": exp_stmts[0][0] if exp_stmts else ""
            }],
            "env_name": env_name,
            "env_desc": env_desc
        }

    exp_keys = [s[2] for s in exp_stmts]
    user_keys = [s[2] for s in user_stmts]

    matcher = difflib.SequenceMatcher(None, exp_keys, user_keys)
    errors = []
    matched_count = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            matched_count += (i2 - i1)
        elif tag == "replace":
            e_range = list(range(i1, i2))
            u_range = list(range(j1, j2))
            common_len = min(len(e_range), len(u_range))
            for k in range(common_len):
                e_idx = e_range[k]
                u_idx = u_range[k]
                exp_raw, _, e_toks = exp_stmts[e_idx]
                user_raw, _, u_toks = user_stmts[u_idx]
                msg = diagnose_mismatch(user_raw, exp_raw, list(u_toks), list(e_toks))
                errors.append({
                    "type": "mismatch",
                    "env": exp_envs[e_idx],
                    "user_line_no": u_idx + 1,
                    "user_line": user_raw,
                    "expected_line": exp_raw,
                    "message": msg
                })
            for k in range(common_len, len(e_range)):
                e_idx = e_range[k]
                errors.append({
                    "type": "missing",
                    "env": exp_envs[e_idx],
                    "expected_line": exp_stmts[e_idx][0],
                    "message": f"Пропущена строка: <code>{exp_stmts[e_idx][0]}</code>"
                })
            for k in range(common_len, len(u_range)):
                u_idx = u_range[k]
                errors.append({
                    "type": "extra",
                    "env": exp_envs[e_range[-1]] if e_range else curr,
                    "user_line_no": u_idx + 1,
                    "user_line": user_stmts[u_idx][0],
                    "message": f"Лишняя строка: <code>{user_stmts[u_idx][0]}</code>"
                })
        elif tag == "delete":
            for e_idx in range(i1, i2):
                errors.append({
                    "type": "missing",
                    "env": exp_envs[e_idx],
                    "expected_line": exp_stmts[e_idx][0],
                    "message": f"Пропущена строка: <code>{exp_stmts[e_idx][0]}</code>"
                })
        elif tag == "insert":
            for u_idx in range(j1, j2):
                errors.append({
                    "type": "extra",
                    "env": curr,
                    "user_line_no": u_idx + 1,
                    "user_line": user_stmts[u_idx][0],
                    "message": f"Лишняя строка: <code>{user_stmts[u_idx][0]}</code>"
                })

    total_expected = len(exp_stmts)
    accuracy = round((matched_count / max(total_expected, 1)) * 100, 1)
    is_correct = (len(errors) == 0 and matched_count == total_expected)

    return {
        "is_correct": is_correct,
        "accuracy": accuracy,
        "matched_count": matched_count,
        "total_expected": total_expected,
        "errors": errors,
        "env_name": env_name,
        "env_desc": env_desc
    }

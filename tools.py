# tools.py
import re
import json
import math
import wikipedia

wikipedia.set_lang("en")

class CalculatorTool:
    name = "calculator"
    description = "Performs safe arithmetic evaluations."

    def run(self, expr: str) -> str:
        """
        expr: a clean Python arithmetic expression like "25*(15/3)" or "2+2"
        returns: string of result or error
        """
        try:
            # safe eval: allow math functions
            safe_locals = {k: getattr(math, k) for k in dir(math) if not k.startswith("")}
            result = eval(expr, {"_builtins_": None}, safe_locals)
            # normalize floats that are integers
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(result)
        except Exception as e:
            return f"Calculator Error: {e}"


class WikipediaTool:
    name = "wikipedia"
    description = "Search Wikipedia and return structured info (tries to return person for 'Who is X of Y' queries)."

    def _find_person_for_role(self, role: str, entity: str):
        """
        Heuristic search to find the incumbent (person) for queries like:
          'Who is the president of India?'
        Returns JSON string: {"type":"person","name": "...", "summary": "..."}
        """
        role = role.strip()
        entity = entity.strip()

        # Try variations targeted at current/incumbent
        variants = [
            f"current {role} of {entity}",
            f"incumbent {role} of {entity}",
            f"{role} of {entity}",
            f"List of {role} of {entity}",
            f"{entity} {role}"
        ]

        for v in variants:
            try:
                hits = wikipedia.search(v, results=6)
            except Exception:
                hits = []
            for title in hits:
                # skip pages that obviously describe an office (have 'List of' or 'office' words)
                if re.search(r'list of|office of|timeline|history', title, flags=re.I):
                    continue
                try:
                    summary = wikipedia.summary(title, sentences=2)
                except Exception:
                    continue
                # If the summary mentions the role and the page looks like a person, accept it
                if re.search(fr'\b{role}\b', summary, flags=re.I) and re.match(r'^[A-Z][\w\s\-\.]+', title):
                    # Likely we found a person page
                    return {"type": "person", "name": title, "summary": summary}
        return None

    def run(self, query: str) -> str:
        """
        Returns JSON string with either:
        - {"type":"person","name": "...","summary":"..."}
        - {"type":"summary","title":"...","summary":"..."}
        - {"type":"error","message":"..."}
        """
        q = query.strip()

        # detect "Who is the <role> of <entity>?" pattern
        m = re.search(r'who\s+is\s+the\s+(.+?)\s+of\s+([^\?\.]+)', q, flags=re.I)
        if m:
            role = m.group(1).strip()
            entity = m.group(2).strip()
            found = self._find_person_for_role(role, entity)
            if found:
                return json.dumps(found, ensure_ascii=False)

            # fallback: try explicit "current <role> of <entity>"
            try:
                fallback_query = f"current {role} of {entity}"
                hits = wikipedia.search(fallback_query, results=5)
                if hits:
                    title = hits[0]
                    summary = wikipedia.summary(title, sentences=2)
                    # maybe the first hit is a person
                    return json.dumps({"type": "person", "name": title, "summary": summary}, ensure_ascii=False)
            except Exception:
                pass

        # generic search: return the summary of the best-matching page
        try:
            hits = wikipedia.search(q, results=5)
            if not hits:
                return json.dumps({"type": "error", "message": f"No wikipedia results for '{q}'"}, ensure_ascii=False)
            title = hits[0]
            summary = wikipedia.summary(title, sentences=3)
            return json.dumps({"type": "summary", "title": title, "summary": summary}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import anthropic

app = Flask(__name__)
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = (
    "Voce e um tecnico senior de bancada, especialista em manutencao de TVs "
    "LED, LCD e Plasma de todas as marcas, com foco principal em defeitos de "
    "display: painel, backlight, T-CON, cabo flat/LVDS, uniformidade, imagem "
    "fantasma, pixels e zonas de dimming. Responda sempre em portugues do "
    "Brasil, de forma tecnica, direta e pratica, como um colega de bancada "
    "orientando outro tecnico. De passos de teste concretos com multimetro "
    "ou inspecao visual sempre que possivel. Se o defeito for fisico no "
    "painel sem reparo de componente, diga isso claramente e sugira "
    "reaproveitamento de pecas boas."
)

@app.route("/expert", methods=["POST"])
def expert():
    data = request.get_json(force=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "mensagem vazia"}), 400

    messages = []
    for turn in history[-10:]:
        role = "user" if turn.get("who") == "user" else "assistant"
        messages.append({"role": role, "content": turn.get("text", "")})
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        reply_text = response.content[0].text
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"reply": reply_text})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

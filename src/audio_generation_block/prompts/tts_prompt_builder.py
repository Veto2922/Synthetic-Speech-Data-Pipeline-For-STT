class TTSPromptBuilder:
    @staticmethod
    def build(data: dict) -> str:
        emotion = data["emotion"]
        style = data["speaker_style"]
        rate = data["speaking_rate"]
        energy = data["energy"]

        text = data["text"]

        prompt = f"""
{emotion}, {style}, {rate}, {energy}.

Say in Egyptian Arabic:
{text}
"""

        return prompt.strip()

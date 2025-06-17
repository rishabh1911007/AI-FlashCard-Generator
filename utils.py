# utils.py

import pandas as pd
import io


def export_to_csv(flashcards):
    df = pd.DataFrame(flashcards)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

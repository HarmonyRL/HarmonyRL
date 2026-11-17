# HarmonyRL

[English](README.md) | 한국어

멜로디에 맞는 코드 진행을 만듭니다. HarmonyRL은 MusicXML이나 MIDI에서 리드시트를 읽어 멜로디 밑에
코드를 쓰고, 나머지는 그대로 두고 고른 마디만 다시 뽑을 수 있습니다.

모델은 사람 반주로 사전학습한 뒤 강화학습으로 미세조정한 Transformer 코드 정책입니다. 원하는
소리의 모델을 고르세요.

| 모델 | 스타일 |
|---|---|
| [`CloudHolic/harmonyrl-chromatic`](https://huggingface.co/CloudHolic/harmonyrl-chromatic) | 조성 밖 코드가 많은 풍부한 리하모니제이션 |
| [`CloudHolic/harmonyrl-smooth`](https://huggingface.co/CloudHolic/harmonyrl-smooth) | 협화적이고 해결되는 진행 |
| [`CloudHolic/harmonyrl-base`](https://huggingface.co/CloudHolic/harmonyrl-base) | 학습 데이터에 가까움 |

각 모델 카드에 학습과 평가가 설명되어 있습니다.

## 설치

Python 3.12 이상.

```sh
pip install harmonyrl
```

PyTorch가 GPU를 찾으면 GPU를 쓰고, CPU에서도 동작합니다.

## 사용법

```python
from pathlib import Path

from harmonyrl import HarmonyRL
from harmonyrl.ingest import read_lead_sheet
from harmonyrl.render import write_lead_sheet

model = HarmonyRL.from_pretrained("CloudHolic/harmonyrl-chromatic")
sheet = read_lead_sheet(Path("melody.musicxml")).sheet

# Up to 3 different harmonizations of the whole lead sheet
candidates = model.harmonize_sheet(sheet, candidates=3, seed=0)
write_lead_sheet(candidates[0], Path("harmonized.musicxml"))

# Redraw bars 4 and 5 (counted from 0) and keep every other chord
redrawn = model.harmonize_sheet(candidates[0], bars=range(4, 6), candidates=2)
write_lead_sheet(redrawn[0], Path("redrawn.mid"))
```

이미 코드 심벌이 있는 리드시트도 같은 방식으로 씁니다. 읽은 뒤 `bars=`를 주면 그 마디만
채웁니다. `bars=` 없이 부르면 모든 코드를 새로 씁니다.

### 생성 설정

각 모델은 기본값을 `generation_config.json`에 담아 배포합니다. 키워드 인자는 그 호출에서만 기본값을
덮어쓰고, `model.generation_config`는 이후 호출에 쓸 값을 유지합니다.

| 설정 | 의미 |
|---|---|
| `temperature` | 샘플링 온도. 낮을수록 안전하고, 높을수록 다양합니다 |
| `pool` | 유지하는 코드 사이의 마디를 다시 채울 때 후보 하나당 뽑는 초안 수. 그 마디 뒤의 코드가 어떤 초안을 돌려줄지 가늠합니다 |
| `max_duplicates` | 서로 다른 후보를 찾는 탐색이 멈추기 전까지 허용하는 중복 뽑기 수 |

```python
model.harmonize_sheet(sheet, candidates=4, temperature=0.8)
```

후보는 항상 서로 다르므로, 호출은 `candidates`(최대 16)보다 적게 돌려줄 수 있습니다. 
후보를 찾는 과정에서 중복된 후보의 개수가 `max_duplicates`(기본 1)에 도달하면 그때까지 찾은 후보만 리턴합니다.
유지하는 코드 사이의 마디가 몇 개뿐이면 서로 다른 진행이 적은 경우가 많으니,
더 오래 찾으려면 `max_duplicates`를 올리세요. `seed`를 주면 같은 장치에서 호출 결과가 재현됩니다.

### 멜로디와 코드를 데이터로 다루기

`HarmonyRL.harmonize`는 32마디 이하의 `Melody` 하나를 받아, `ChordEvent` 튜플을 최대
`candidates`개 담은 리스트를 돌려줍니다. 두 타입은 `harmonyrl.schema`에 있습니다.
`harmonize_sheet`는 더 긴 구간을 겹치는 32마디 창(`overlap=`, 기본 4마디)으로 나눠 창마다
`harmonize`를 부릅니다.

## 파일

| 형식 | 읽기 | 쓰기 |
|---|---|---|
| MusicXML (`.musicxml`, `.xml`; `.mxl`은 읽기만) | 멜로디와 코드 심벌 | 멜로디와 코드 심벌 |
| MIDI (`.mid`, `.midi`) | 멜로디 | 멜로디와 코드 |

- 악보는 박자표가 바뀌는 곳과, MusicXML에서는 리허설 마크에서 구간으로 나뉩니다. `bars=`의 마디
  번호는 모든 구간에 걸쳐 셉니다.
- `read_lead_sheet(path, part=...)`로 멜로디가 있는 파트(MusicXML)나 트랙(MIDI)을 고릅니다.
  주지 않으면 가장 멜로디다운 것을 고릅니다.
- 곡 전체에 조성 하나를 조표와 음으로 정합니다. 조표가 실제 음악과 다르면 `key=`를 주세요.
- 모델이 정확히 표기할 수 없는 코드 심벌은 근사하고, 그 마디를 `SheetImport.approximated`에
  남깁니다. 반복 기호는 펼치지 않고 적힌 대로 읽으며, `SheetImport.warnings`에 알립니다.
- 여러 번에 걸쳐 코드를 다듬으려면 MusicXML로 쓰고 다시 읽으세요. MIDI 출력에는 코드가 음표로만
  남습니다.

## 한계

- `harmonize` 한 번은 32마디까지 다루고, `harmonize_sheet`의 창은 겹치는 부분 너머로는 서로를 보지
  못하므로 반복되는 절 같은 곡 전체의 구조는 모델링하지 않습니다.
- 새 코드가 주변의 유지된 코드와 어울리지 않고 튈 수 있습니다. 다시 뽑거나 후보를 더 요청하세요.
- 하모나이제이션은 매번 샘플이라, `seed`를 주지 않으면 뽑을 때마다 결과가 다릅니다.

## 라이선스

코드는 MIT 라이선스입니다. 모델 가중치는 학습 데이터를 따라 CC BY-NC-SA 3.0입니다. 학습 데이터는
[Sheet Sage](https://github.com/chrisdonahue/sheetsage)와 함께 공개된
[Hooktheory](https://www.hooktheory.com)의 멜로디와 코드입니다(Donahue, Thickstun, Liang,
"[Melody Transcription via Generative Pre-Training](https://arxiv.org/abs/2212.01884)",
ISMIR 2022).

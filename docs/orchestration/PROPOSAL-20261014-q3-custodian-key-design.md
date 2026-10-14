# PROPOSAL 2026-10-14 — Q3 custodian design: Joseph holds an `age` key

**Status: a proposal for Joseph and Ben to review. It is not adopted.** Nothing has been encrypted, generated,
committed or run under it. The only act so far is Joseph's: he made the key pair and gave the director the public key.

**Written by** the paper-tighten lane, as director. It answers the design owed under Q3 in
[`DECISION-20261014-joseph-stage-d-input-answers.md`](DECISION-20261014-joseph-stage-d-input-answers.md). There
Joseph said "there is probably some way I can do this with keys and encryption". The custodial objects come from
[`state/2d-closeout/stageD-inputs/REPORT.md`](state/2d-closeout/stageD-inputs/REPORT.md) §7.

**CITABLE FOR:**
- Joseph's public key;
- the director's checks on the key, listed in §1;
- the proposed commit → freeze → reveal procedure.

**NOT CITABLE FOR:**
- an adopted protocol;
- a Stage D start (Q7 is still open);
- a salt or commitment (none exists yet);
- the fold design: its unit, the number of folds, and which events are assessed. Those belong to the Stage D plan;
- a compute grant.

## 1. The key

| item | value |
|---|---|
| public key (recipient) | `age1c7ssjcx0exu4uv9ymnghfrv3pf3elw03mhxdyh5ghxa99xagd3qqh3zglu` |
| made by | Joseph, 2026-10-14, in his own Terminal: `age-keygen \| age -p -o ~/q3-custodian-key.age` (`age` v1.3.2, Homebrew) |
| private key | `~/q3-custodian-key.age` on Joseph's Mac. It is passphrase-encrypted, so no plaintext copy was ever written |
| director's checks (2026-10-14) | The file is 371 bytes. Its header reads `age-encryption.org/v1` and its first stanza `-> scrypt`, which makes it a passphrase-encrypted file and not a plaintext key. `age -r <public key>` accepts the recipient. Only the header was read. The passphrase is not known to any session |
| backup | Joseph's responsibility. He keeps the key file and the passphrase together, in a password manager or offline. Lose either one and nothing encrypted to this key can be recovered |

## 2. What it protects, and what it cannot

Every lane runs as Joseph: as `josephrb` on the cluster, and as his user on the Mac. Two consequences follow.

- **A secret is safe from the lanes only while it sits encrypted to this key.** At the moment it is decrypted, a
  process running as Joseph holds it in plaintext.
- **So the procedure never computes with a secret while it is still secret.** The salt and the custodian's choices
  stay sealed until the method is frozen. Then they are revealed and published, and only after that does anything
  run on them. The private key is used once, on the Mac, at the reveal.

| protected | not protected |
|---|---|
| the fold salt, and so which events fall in which fold, until the reveal | the events themselves. Every lane can read the AnaTuples |
| the custodian's choices for the fresh independent-generator sample (configuration, seeds, amplitude; Stage D §6.2, §7) until the recipe is frozen | anything Joseph himself reads. He is the analyst too, so this scheme separates the lanes from the custodial secrets, not the analyst from them. A referee who asks for a custodian independent of the analyst would need a different holder (§5) |
| proof that the split was fixed before development: the published sha256 of a 256-bit random salt reveals nothing about it, and it cannot be changed afterwards | a reveal run while a session is active. Its plaintext is readable by that session |

## 3. Procedure

Each step that uses the passphrase or the plaintext is Joseph's. He runs it in a Terminal he opened himself, never
through a session's `!` prompt, since whatever is typed there is visible to the session.

**S1. Salt and commitment (Joseph).** The commands below were rehearsed by the director in zsh with a throwaway key
on 2026-10-14. The sha256 of the salt agreed before encryption and after decryption, and the salt is 64 hex
characters.

```
s=$(openssl rand -hex 32)
printf %s "$s" | shasum -a 256
printf %s "$s" | age -r age1c7ssjcx0exu4uv9ymnghfrv3pf3elw03mhxdyh5ghxa99xagd3qqh3zglu -o ~/q3-fold-salt.age
unset s
```

Joseph gives the director the printed sha256. The director records it on main as the commitment, together with the
sha256 of `~/q3-fold-salt.age`. The salt never appears on screen, and it never appears in shell history.

**S2. Fold rule, declared before development.** Membership is a keyed hash of the fold unit, for example the first
8 bytes of `HMAC-SHA256(salt, unit)` taken mod n. The code, the fold unit and n are committed on main and pinned by
sha before any reveal.

The fold unit is the Stage D plan's decision. It may be the event key `K = (mc_run, mc_subrun, mc_nthEvtInFile)`.
It may instead have to be a group of events that share overlaid data gates (Stage D §4.4).

**S3. Method freeze (director record, Joseph's decision).** Before any reveal, everything the assessment will use is
committed on main:
- the code sha and configuration;
- the decision statistic and its thresholds;
- what each outcome means.

Joseph then records the freeze.

**S4. Reveal (Joseph).** No session is running. In his own Terminal, Joseph runs:

```
age -d -i ~/q3-custodian-key.age ~/q3-fold-salt.age | shasum -a 256
```

He types the passphrase, which unlocks the identity, and checks that the printed hash equals the S1 commitment. If
it matches, he decrypts the salt and gives it to the director, who publishes it on main. From that point it is no
longer secret: any lane can form the folds with the frozen S2 code and run the frozen S3 method.

**S5. The independent-generator sample (Stage D §6.2).** The same pattern applies:
- Joseph writes the configuration, seeds and amplitude into a file and encrypts it with `age -r <public key>`;
- the sha256 of the plaintext is committed;
- after the recipe freeze, he reveals the file and generation runs.

Joseph has to choose these himself, without a session. A lane can describe the allowed space of choices; it must not
propose the values.

**Optional: sealed outputs.** If a result has to be computed before the freeze and kept unseen, the job can pipe it
through `age -r <public key>` at write time. Lanes can then create the file but cannot read it. While the job runs,
the plaintext is still in that job's memory, which is the §2 limit.

## 4. What this asks of Joseph

1. Keep the backup (§1).
2. Run S1, S4 and the S5 choices yourself, outside any session.
3. Decide the S3 freeze.
4. Decide whether you as holder are enough, or whether Ben should hold instead (§5).

None of this is due until Stage D proceeds, which waits on Q7.

## 5. Open for the review with Ben

- **Independence of the holder.** With Joseph as holder, the secret is kept from the lanes but not from the analyst.
  - If that is not enough, Ben can make his own `age` key, and the salt can be encrypted to Ben alone.
  - Encrypting to both keys (`-r` twice) lets either holder decrypt. That is not a two-person rule; `age` has no
    threshold mode.
- **Fold unit and n.** Event or overlay-gate group, as in S2. This is Stage D design.
- **Where the public key is used.** It is public. Lanes may use it to encrypt, and it may be committed anywhere.

## 6. Limits

- The procedure was rehearsed with a throwaway key without a passphrase. Unlocking Joseph's passphrase-protected
  identity at S4 has not been exercised. `age` v1.3.2 accepts encrypted identity files with `-i`. Joseph can test
  the round trip himself, on a dummy file, before S1.
- The director did not search the Mac for other copies of the private key. Joseph made it with the encrypted pipeline
  above, which writes no plaintext.

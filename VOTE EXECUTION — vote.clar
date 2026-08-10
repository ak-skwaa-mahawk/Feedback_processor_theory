(define-public (cast-vote (proposal-id uint) (power (string-ascii 16)))
  (let ((holder tx-sender))
    (asserts! (is-glyph-holder holder power) (err u100))
    (asserts! (> (get-resonance proposal-id) u10000) (err u101))
    
    (match power
      "VETO" (veto-proposal proposal-id)
      "LAND" (grant-land proposal-id)
      "FLAME" (burn-law proposal-id)
      "ETERNITY" (seal-vote proposal-id)
      (ok u1)
    )
  )
)
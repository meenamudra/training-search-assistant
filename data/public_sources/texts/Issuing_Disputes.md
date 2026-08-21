# Issuing disputes

Learn how to use Issuing to dispute transactions.

When an issue with a transaction occurs, a user or their cardholder can dispute the charge. Common issues include fraud, product/service not received, or processing error.

Stripe offers a guided Dashboard process and an API to submit disputes and monitor them through to resolution. This process typically takes between 30 and 90 days. If you manage a low volume of disputes, we recommend using the Dashboard. If you manage a high volume of disputes, we recommend using the API.

> You can’t dispute an authorization. Acquiring businesses reverse authorizations at their discretion. You can file a dispute after the authorization is complete and the acquiring business captures the transaction.

## Considerations before initiating a dispute

### Network rules

We process disputes according to rules and guidelines of the card network that handled the transaction. For the complete details regarding the rules and guidelines that apply to disputes, refer to the [Visa](https://usa.visa.com/content/dam/VCOM/download/about-visa/visa-rules-public.pdf) and [Mastercard](https://www.mastercard.us/en-us/business/overview/support/rules.html) rulebooks.

### Submitting valid disputes

You can only submit a dispute once. After submission, you can’t edit the dispute or add supplemental evidence. Users must submit disputes according to card network requirements. Submitting an invalid or incomplete dispute might result in a loss.

### Consumer disputes

For consumer disputes (for example, not received, canceled, not as described), cardholders must attempt to resolve the issue with the business before submitting a dispute. Include documentation of the cardholder’s resolution attempt in the submission.

### How card networks define fraud

For both Visa and Mastercard, a fraudulent transaction is one where the cardholder denies participating in the charge. If the cardholder acknowledges they participated in the transaction (for example, they were victims of a scam), they should file the dispute under a different reason for which they have dispute rights.

### Requirements for fraud disputes (for platforms)

Card networks require fraud reporting. Platforms must allow their connected accounts to submit fraud disputes directly to Stripe through a dashboard that you make available using the Stripe API or embedded components. You can’t restrict their ability to submit fraud disputes in any way. After fraud disputes are submitted, Stripe reviews them to determine whether to reimburse the cardholder.

### Blocked dispute submissions

Stripe might block fraud dispute submission if the transaction doesn’t qualify for fraud protection under local regulations and the account holder has no dispute rights according to network rules.

**For platforms**: If you’re obligated to submit a dispute and do so, you’ve fulfilled your obligation, regardless of whether Stripe blocks the submission.

Card networks might consider a dispute invalid for the following reasons (among others):

- The transaction is a refund and not a [capture](https://docs.stripe.com/issuing/purchases/transactions.md).
- The transaction is a mobile push payment transaction.
- The dispute timeframe has expired.

In the Dashboard, the **Dispute transaction** button is enabled only for eligible transactions. In the API, disputing an ineligible transaction returns an error. For more details about which transactions can’t be disputed, see [Why your dispute might be rejected](https://docs.stripe.com/issuing/purchases/disputes.md#why-your-dispute-might-be-rejected).

### Expiration 

Card networks establish a timeframe by which a dispute can be submitted. A dispute submitted after this timeframe is considered expired and is lost. The timeframe varies depending on dispute reason and the card network.

For Visa, most fraudulent and processing error disputes must be submitted within 110 days of the transaction date, ‘Authorization’ disputes within 65 days, and most consumer disputes such as ‘Canceled’, ‘Not Received’, and ‘Not as Described’ within 110 days of the merchandise or service cancellation or expected delivery date. Mastercard is similar, except ‘Authorization’, ‘Incorrect Amount’, and ‘Duplicate’ disputes must be filed within 80 days of the transaction date.

### Dispute amount 

Disputes can be filed for the full transaction amount or a partial amount. If there are refunds, you must account for them and can file only a partial dispute. For example, if you want to dispute a 100 USD charge but the business has already refunded 30 USD, the maximum amount you can dispute is 70 USD. Certain dispute reasons, such as ‘Incorrect Amount’, require only a partial dispute amount. For many consumer disputes, the dispute amount is partial when part of the order or service was received.

## Lifecycle

In this lifecycle diagram, “business” refers to the acquiring business, the business receiving the payment.

Lifecycle of an Issuing dispute (See full diagram at https://docs.stripe.com/issuing/purchases/disputes)

```text
[Unsubmitted] -- 110 days --> [Expired]
[Unsubmitted] -- Submit --> [Submitted (the dispute is sent to the card network)]
[Submitted (the dispute is sent to the card network)] -- Rejected --> [Lost]
[The business receives the dispute] -- ≤ 30 days --> [The business accepts liabilityor doesn’t respond]
[Submitted (the dispute is sent to the card network)] --> [The business receives the dispute]
[The business receives the dispute] -- ≤ 30 days --> [The business refutes with counter-evidence]
[The business refutes with counter-evidence] -- ≤ 30 days --> [Stripe refutes the business’s evidence]
[The business accepts liabilityor doesn’t respond] --> [Won]
[The business refutes with counter-evidence] --> [Evidence in favor ofacquiring business]
[The card network makes a final ruling] --> [Won]
[Evidence in favor ofacquiring business] --> [Lost]
[The card network makes a final ruling] --> [Lost]
[Stripe refutes the business’s evidence] -- ≤ 30 days --> [The business declines, moves toarbitration with card network]
[Stripe refutes the business’s evidence] -- ≤ 30 days --> [The business accepts liabilityor doesn’t respond]
[The business declines, moves toarbitration with card network] -- ≤ 30 days --> [The card network makes a final ruling]
```

Newly-created disputes begin in an `unsubmitted` status. At this point, you can update their evidence and metadata. After you’ve added all the required evidence, you can then submit the dispute. If you don’t submit a dispute within 110 days of the transaction clearing, its status becomes `expired`.

Stripe and card networks process disputes that have a status of `submitted`. As such, you can’t update dispute evidence, but you can still update their `metadata`. Submitted disputes enter into a multi-step process defined by card networks and participating banks. After a dispute is resolved, Stripe transitions it to either the terminal `won` or `lost` status.

If a dispute is won, you must reimburse the cardholder. If a dispute is lost, you can choose whether to reimburse the cardholder.

## Additional regulation protection and liability for fraud (US platforms)

Some cardholders might be eligible for additional regulation protection depending on their account, location, and/or card type.

### The Truth in Lending Act and Regulation Z

The Truth in Lending Act and its implementing regulation, Regulation Z, are federal rules that apply to various credit products, including credit cards. This regulation establishes rights for some disputes and offers additional credit card protections.

Most aspects of Regulation Z don’t apply to business-purpose cards, but it does protect those cardholders from fraud and other types of “unauthorized use,” which means use of a credit card by someone without authorization to use it and from which the cardholder receives no benefit. Regulation Z generally caps a cardholder’s liability for unauthorized use at 50 USD.

### The Electronic Funds Transfer Act and Regulation E

The Electronic Fund Transfer Act and its implementing regulation, Regulation E, protect consumer cardholders engaged in electronic fund transfers by establishing rights, liabilities, and responsibilities for the transaction’s participants. It governs transactions made with various consumer electronic funds transfer products, including debit cards, and provides cardholders with additional protection across a variety of different dispute conditions.

Regulation E might require Stripe to issue provisional credit to cardholders, depending on the length of the dispute investigation (which can take 45 or 90 days, depending on the case). If the dispute isn’t resolved within the required timeframe, the provisional credit becomes permanent.

### Reasonable investigation

When a cardholder disputes a transaction, Stripe sends the dispute to the card network for adjudication. During the chargeback process, if Stripe can’t disprove liability, the dispute might enter arbitration, where the card network ultimately determines who must pay for the fraud: you or the business.

If Stripe or the card network determines that the business is liable, you and your cardholder aren’t responsible for the disputed transaction.

If Stripe or the card network determines that you’re liable, Stripe investigates whether the cardholder qualifies for additional regulatory protection. If the dispute is valid and the cardholder qualifies for protection, you might remain liable for the unauthorized transactions. If the dispute is invalid or the cardholder doesn’t qualify for protection, we hold the cardholder responsible for the charge.

## Why your dispute might be rejected 

A dispute might be rejected in Stripe for several reasons, including:

- **Dispute will be rejected by the network because the e-commerce condition is secured**: This fraud dispute is invalid because the card network has indicated the transaction was securely authenticated.
- **Dispute is invalid under Dispute condition 10.3 as the transaction was electronically read**: This dispute is invalid because the transaction was authorized at a card terminal that accepts chip.
- **Dispute is invalid as this transaction was approved after a prior fraud dispute or fraud report**: The cardholder didn’t deactivate the card after claiming fraud on previous transactions.
- **Dispute is invalid as more than 35 disputes were processed within 120 calendar days of this dispute**: This fraud dispute is invalid because more than 35 fraud disputes have been submitted on the same card within the past 120 calendar days.
- **Transaction is less than the minimum amount required**: This dispute hasn’t met the minimum amount threshold set by the card network.

If your dispute is rejected, it eventually transitions to an `expired` status.

## Lost disputes 

The reason a dispute is lost depends on the reason it was submitted. Some common reasons a dispute might be lost include:

### Reasons that affect all dispute conditions

- The entire transaction amount was disputed when a partial (or full) refund was issued.
- The dispute was submitted outside the allowed timeframe. For more details, see [Expiration](https://docs.stripe.com/issuing/purchases/disputes.md#expiration).

### Fraudulent

- The business was able to prove the cardholder participated in the transaction.

### Canceled

- The business was able to prove the cardholder never attempted to cancel or return the purchase.
- The business was able to prove the cardholder agreed to a no-refund cancellation policy or attempted to return outside the cancellation policy period.

### Duplicate

- The business was able to prove both transactions were for different purchases.
- The business was able to provide proof the customer was charged the agreed price.

### Not as described

- The business was able to provide proof the service or merchandise received was as described.
- The business was able to provide proof the service or merchandise received wasn’t damaged.
- The business was able to provide proof the cardholder never attempted to return the merchandise, or refused to return the merchandise.
- The business was able to provide proof the cardholder used the service without attempting to cancel.

### Not received

- The business was able to provide proof the cardholder received the purchase.

### No valid authorization

- The business was able to provide proof that a valid authorization was captured.

### Other

- The dispute didn’t meet any of the card network’s accepted dispute conditions.
- The business was able to disprove liability depending on the situation.
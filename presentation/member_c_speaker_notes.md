# Member C Presentation Script

## Slide 1 - Opening

Hi everyone, I will present Member C, which is the evaluation metrics part of our project.

My goal was not to build another classifier. My role was to test whether the aspect labels from Member B actually help retrieval.

So I compared the original BM25 ranking with an aspect-aware reranking over 35 queries, 6 games, and 2100 retrieved reviews.

## Slide 2 - Evaluation Design

The evaluation uses two inputs.

First, Member A provides the BM25 top-10 retrieved reviews for every query-game pair.

Second, Member B provides predicted aspect labels for each retrieved review.

For Member C, I define binary aspect relevance. If the target query aspect appears in the predicted aspects of a review, relevance is 1. Otherwise, relevance is 0.

Then the aspect-aware reranker promotes reviews that match the query aspect, and uses BM25 score as the second sorting signal.

## Slide 3 - Metric and Test

The main metric is nDCG at 10.

This metric is useful because we care not only whether relevant reviews are retrieved, but whether they appear near the top of the ranking.

I compute nDCG at 10 for each query-game group, then average across all 210 groups.

I also use a paired permutation test, because BM25 and the reranked system are evaluated on the same query-game groups.

## Slide 4 - Main Result

The main result is that aspect-aware reranking improves mean nDCG at 10 from 0.8756 to 0.9810.

The mean improvement is 0.1053.

The paired permutation test gives a p-value of 0.0001, so the improvement is statistically significant.

This suggests that using aspect labels makes the ranking better aligned with the user's intended aspect, instead of relying only on keyword similarity.

## Slide 5 - Per-Aspect Pattern

When we look at each aspect separately, the reranker improves every evaluated aspect.

The largest gains are for price and controls.

Graphics, price, and story reach perfect mean nDCG in this setup after reranking.

So the improvement is not only caused by one category. It supports the idea that aspect labels provide useful retrieval context across different types of review questions.

## Slide 6 - Conclusion and Caveats

To conclude, Member C shows that aspect-aware reranking improves retrieval quality in our experiment.

The result supports our project idea: LLM aspect labels can be used as an information retrieval signal to improve context.

The main caveat is that our relevance signal comes from LLM-predicted aspects, not full human retrieval judgments.

Member B validated the classifier on 230 gold reviews, with the best model reaching kappa 0.540, so the signal is reasonable, but it is still not perfect.

Because of that, I would describe this as an aspect-consistency evaluation rather than a complete human relevance evaluation.

My takeaway is: adding aspect labels gives the retrieval system better context for ranking game reviews.

## Very Short Backup Version

If I need to say this faster:

Member C evaluates whether aspect-aware reranking improves retrieval. I used Member A's BM25 results and Member B's predicted aspect labels. A review is relevant if its predicted aspects contain the query aspect. Using nDCG at 10 over 210 query-game groups, BM25 scored 0.8756 and aspect-aware reranking scored 0.9810, with a significant improvement of 0.1053 and p = 0.0001. The main limitation is that relevance is based on predicted aspect labels rather than full human retrieval judgments, so we call this aspect-consistency evaluation.

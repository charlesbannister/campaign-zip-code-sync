"""holds ENUM_MAP variable which is a dictionary used to map googe ads api enums form int values to
names"""
from google.ads.googleads.v20.enums.types import (
    gender_type,
    day_of_week,
    customer_status,
    advertising_channel_sub_type,
    advertising_channel_type,
    ad_network_type,
    campaign_experiment_type,
    bidding_strategy_type,
    campaign_status,
    campaign_serving_status,
    ad_group_status,
    campaign_status,
    keyword_match_type,
    ad_group_criterion_status,
    quality_score_bucket,
    ad_group_ad_status,
    ad_type,
    ad_strength,
    device,
    policy_approval_status,
    policy_review_status,
    shared_set_status,
    shared_set_type,
    campaign_shared_set_status,
    search_term_targeting_status,
    budget_status,
)

enum_map = {
    "campaign_criterion.ad_schedule.day_of_week": lambda value: day_of_week.DayOfWeekEnum.DayOfWeek(value).name
    if value is not None
    else None,
    "ad_group_criterion.gender.type": lambda value: gender_type.GenderTypeEnum.GenderType(value).name
    if value is not None
    else None,
    "segments.ad_network_type": lambda value: ad_network_type.AdNetworkTypeEnum.AdNetworkType(value).name
    if value is not None
    else None,
    "customer.status": lambda value: customer_status.CustomerStatusEnum.CustomerStatus(value).name
    if value is not None
    else None,
    "campaign.advertising_channel_sub_type": lambda value: advertising_channel_sub_type.AdvertisingChannelSubTypeEnum.AdvertisingChannelSubType(
        value
    ).name
    if value is not None
    else None,
    "campaign.advertising_channel_type": lambda value: advertising_channel_type.AdvertisingChannelTypeEnum.AdvertisingChannelType(
        value
    ).name
    if value is not None
    else None,
    "campaign.experiment_type": lambda value: campaign_experiment_type.CampaignExperimentTypeEnum.CampaignExperimentType(
        value
    ).name
    if value is not None
    else None,
    "bidding_strategy.type": lambda value: bidding_strategy_type.BiddingStrategyTypeEnum.BiddingStrategyType(
        value
    ).name
    if value is not None
    else None,
    "campaign.status": lambda value: campaign_status.CampaignStatusEnum.CampaignStatus(value).name
    if value is not None
    else None,
    "campaign.serving_status": lambda value: campaign_serving_status.CampaignServingStatusEnum.CampaignServingStatus(
        value
    ).name
    if value is not None
    else None,
    "ad_group.status": lambda value: ad_group_status.AdGroupStatusEnum.AdGroupStatus(value).name
    if value is not None
    else None,
    "ad_group_criterion.keyword.match_type": lambda value: keyword_match_type.KeywordMatchTypeEnum.KeywordMatchType(
        value
    ).name
    if value is not None
    else None,
    "ad_group_criterion.status": lambda value: ad_group_criterion_status.AdGroupCriterionStatusEnum.AdGroupCriterionStatus(
        value
    ).name
    if value is not None
    else None,
    "ad_group_criterion.quality_info.creative_quality_score": lambda value: quality_score_bucket.QualityScoreBucketEnum.QualityScoreBucket(
        value
    ).name
    if value is not None
    else None,
    "campaign_criterion.keyword.match_type": lambda value: keyword_match_type.KeywordMatchTypeEnum.KeywordMatchType(
        value
    ).name
    if value is not None
    else None,
    "ad_group_criterion.keyword.match_type": lambda value: keyword_match_type.KeywordMatchTypeEnum.KeywordMatchType(
        value
    ).name
    if value is not None
    else None,
    "shared_criterion.keyword.match_type": lambda value: keyword_match_type.KeywordMatchTypeEnum.KeywordMatchType(
        value
    ).name
    if value is not None
    else None,
    "ad_group_ad.status": lambda value: ad_group_ad_status.AdGroupAdStatusEnum.AdGroupAdStatus(
        value
    ).name
    if value is not None
    else None,
    "ad_group_ad.ad.type": lambda value: ad_type.AdTypeEnum.AdType(value).name
    if value is not None
    else None,
    "ad_group_ad.ad.stregth": lambda value: ad_strength.AdStrengthEnum.AdStrength(value).name
    if value is not None
    else None,
    "ad_group_ad.policy_summary.approval_status": lambda value: policy_approval_status.PolicyApprovalStatusEnum.PolicyApprovalStatus(
        value
    ).name
    if value is not None
    else None,
    "ad_group_ad.policy_summary.review_status": lambda value: policy_review_status.PolicyReviewStatusEnum.PolicyReviewStatus(
        value
    ).name
    if value is not None
    else None,
    "ad_group_ad.ad.device_preference": lambda value: device.DeviceEnum.Device(value).name
    if value is not None
    else None,
    "search_term_view.status": lambda value: search_term_targeting_status.SearchTermTargetingStatusEnum.SearchTermTargetingStatus(
        value
    ).name
    if value is not None
    else None,
    "shared_set.status": lambda value: shared_set_status.SharedSetStatusEnum.SharedSetStatus(
        value
    ).name
    if value is not None
    else None,
    "shared_set.type": lambda value: shared_set_type.SharedSetTypeEnum.SharedSetType(value).name
    if value is not None
    else None,
    "campaign_shared_set.status": lambda value: campaign_shared_set_status.CampaignSharedSetStatusEnum.CampaignSharedSetStatus(
        value
    ).name
    if value is not None
    else None,
    "segments.device": lambda value: device.DeviceEnum.Device(value).name
    if value is not None
    else None,
    "campaign_budget.status": lambda value: budget_status.BudgetStatusEnum.BudgetStatus(value).name
    if value is not None
    else None,
    "campaign.bidding_strategy.type": lambda value: bidding_strategy_type.BiddingStrategyTypeEnum.BiddingStrategyType(
        value
    ).name
    if value is not None
    else None,
}

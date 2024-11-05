/** get "learn more" link based on category */
export const learnMoreLink = (category: string) => {
  switch (category) {
    case "cancerincidence":
    case "cancermortality":
      return "/sources#cancer-incidence-and-mortality";
    case "sociodemographics":
    case "economy":
    case "housingtrans":
      return "/sources#sociodemographics-economics-insurance-and-housing-transportation";
    case "rfandscreening":
      return "/sources#screening-risk-factors-and-other-health-factors";
    case "environment":
      return "/sources#environment";
    case "cancerdisparitiesindex":
      return "/sources#cancer-disparities-index";
  }

  return "/sources";
};

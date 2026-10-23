/* Parse both paste columns before filtering or deduplicating any URLs. */
(function (root) {
  function lines(text) {
    const rows = String(text || "").split(/\r\n|\n|\r/).map((row) => row.trim());
    while (rows.length && !rows[0]) rows.shift();
    while (rows.length && !rows[rows.length - 1]) rows.pop();
    return rows;
  }

  function parse(rawUrls, rawCompanies) {
    const companyNames = lines(rawCompanies);
    const hasCompanies = companyNames.length > 0;
    const urlRows = lines(rawUrls);
    const urlPattern = /https?:\/\/(?:[a-z0-9-]+\.)?linkedin\.com\/in\/[^\s,;]+/gi;
    const urls = hasCompanies
      ? urlRows.map((url) => url.replace(/[),.;]+$/g, ""))
      : (String(rawUrls || "").match(urlPattern) || []).map((url) => url.replace(/[),.;]+$/g, ""));
    let error = "";
    if (hasCompanies) {
      const invalid = urls.findIndex((url) => {
        const matches = url.match(urlPattern) || [];
        return matches.length !== 1 || matches[0] !== url;
      });
      const blankCompany = companyNames.findIndex((name) => !name);
      const invalidCompany = companyNames.findIndex((name) => name.length > 200 || name.includes("\t"));
      if (invalid >= 0) error = `URL row ${invalid + 1}: enter one LinkedIn profile URL per line.`;
      else if (blankCompany >= 0) error = `Company row ${blankCompany + 1} is empty. Fill it in to keep the rows aligned.`;
      else if (invalidCompany >= 0) error = `Company row ${invalidCompany + 1}: enter one name, up to 200 characters.`;
      else if (urls.length !== companyNames.length) error = `${urls.length} URLs and ${companyNames.length} companies — the counts must match.`;
    }
    return {urls, companyNames: hasCompanies ? companyNames : null, error};
  }

  function preview(rawUrls, rawCompanies) {
    const result = parse(rawUrls, rawCompanies);
    const companies = result.companyNames || [];
    const rows = Array.from({length: Math.max(result.urls.length, companies.length)}, (_, index) => {
      const url = result.urls[index] || "";
      const company = companies[index] || "";
      return {url, company};
    });
    return {...result, rows};
  }

  root.ConnectInput = {parse, preview};
})(globalThis);

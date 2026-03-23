function formatValidationItem(item) {
  if (!item || typeof item !== "object") return null

  const msg = typeof item.msg === "string" ? item.msg : null
  const locParts = Array.isArray(item.loc)
    ? item.loc.filter((part) => typeof part === "string" && part !== "body")
    : []
  const loc = locParts.length ? locParts.join(".") : null

  if (loc && msg) return `${loc}: ${msg}`
  if (msg) return msg
  return null
}

function normalizeDetail(detail) {
  if (!detail) return null
  if (typeof detail === "string") return detail

  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => normalizeDetail(item))
      .filter((part) => typeof part === "string" && part.trim().length > 0)

    if (parts.length) return parts.join(" | ")
    return null
  }

  if (typeof detail === "object") {
    const validationMsg = formatValidationItem(detail)
    if (validationMsg) return validationMsg

    if (typeof detail.detail === "string") return detail.detail
    if (detail.detail) {
      const nested = normalizeDetail(detail.detail)
      if (nested) return nested
    }

    if (typeof detail.message === "string") return detail.message
  }

  return null
}

export function getApiErrorMessage(error, fallback = "Something went wrong") {
  const apiPayload = error?.response?.data
  const message =
    normalizeDetail(apiPayload?.detail) ??
    normalizeDetail(apiPayload?.message) ??
    normalizeDetail(error?.message)

  return message || fallback
}


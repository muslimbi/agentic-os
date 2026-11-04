import { renderPlaceholder } from "../utils.js";
export function render() {
  return renderPlaceholder("Setup wizard", "A future guided setup for a local or hybrid deployment.", ["Environment checks", "Root identity and policy", "Provider and storage configuration"]);
}

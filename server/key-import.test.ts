import { describe, expect, it } from "vitest";
import { parseImportedCodes } from "./routers";

describe("parseImportedCodes", () => {
  it("accepts one key per line, trims spaces and removes duplicates", () => {
    expect(parseImportedCodes("  Teste key  \nTESTE-002\nTeste key\n")).toEqual(["Teste key", "TESTE-002"]);
  });

  it("does not split spaces inside a key", () => {
    expect(parseImportedCodes("Minha Key Manual")).toEqual(["Minha Key Manual"]);
  });
});

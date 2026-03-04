import { describe, it, expect } from "vitest";
import { maskSensitive } from "../src/mask-sensitive.js";

describe("maskSensitive", () => {
  it("masks Bearer tokens", () => {
    const input = 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.test.signature';
    const { masked, redactionCount } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:token]");
    expect(masked).not.toContain("eyJhbGciOiJIUzI1NiJ9");
    expect(redactionCount).toBe(1);
  });

  it("masks API key parameters while preserving key name", () => {
    const input = 'api_key=sk_live_abc123def456ghi789';
    const { masked } = maskSensitive(input);
    expect(masked).toContain("api_key=");
    expect(masked).toContain("[REDACTED:credential]");
    expect(masked).not.toContain("sk_live_abc123def456ghi789");
  });

  it("masks connection strings", () => {
    const input = 'DATABASE_URL=postgres://user:p4ssw0rd@db.example.com:5432/mydb';
    const { masked } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:connection-string]");
    expect(masked).not.toContain("p4ssw0rd");
  });

  it("masks connection strings with empty username", () => {
    const input = 'REDIS_URL=redis://:s3cret@redis.example.com:6379/0';
    const { masked } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:connection-string]");
    expect(masked).not.toContain("s3cret");
  });

  it("masks AWS access keys", () => {
    const input = 'aws_key=AKIAIOSFODNN7EXAMPLE';
    const { masked } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:");
    expect(masked).not.toContain("AKIAIOSFODNN7EXAMPLE");
  });

  it("masks private key blocks", () => {
    const input = `-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn
-----END RSA PRIVATE KEY-----`;
    const { masked } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:private-key]");
    expect(masked).not.toContain("MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn");
  });

  it("masks unterminated private key blocks", () => {
    const input = `-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQ...`;
    const { masked, redactionCount } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:private-key]");
    expect(masked).not.toContain("MIIEvQIBADANBgkqhkiG9w0BAQ");
    expect(redactionCount).toBeGreaterThanOrEqual(1);
  });

  it("masks private key with non-matching END marker in between", () => {
    const input = `-----BEGIN RSA PRIVATE KEY-----\nMIIE...secret...\n-----END CERTIFICATE-----\nmore_key_data\n-----END RSA PRIVATE KEY-----`;
    const { masked } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:private-key]");
    expect(masked).not.toContain("MIIE...secret...");
    expect(masked).not.toContain("more_key_data");
  });

  it("masks short credential values", () => {
    const input = 'token=abc1234';
    const { masked } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:credential]");
    expect(masked).not.toContain("abc1234");
  });

  it("masks double-quoted credential values with commas", () => {
    const input = 'token="abc,def,ghi"';
    const { masked } = maskSensitive(input);
    expect(masked).toBe('token="[REDACTED:credential]"');
  });

  it("masks single-quoted credential values", () => {
    const input = "secret='my,secret,value'";
    const { masked } = maskSensitive(input);
    expect(masked).toBe("secret='[REDACTED:credential]'");
  });

  it("masks credential values with escaped quotes", () => {
    const input = 'token="ab\\"cd,ef"';
    const { masked } = maskSensitive(input);
    expect(masked).toBe('token="[REDACTED:credential]"');
  });

  it("masks generic long secret in double quotes with comma", () => {
    const input = 'KEY="abcdefghijklmnopqrst,uvw"';
    const { masked } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:");
    expect(masked).not.toContain("abcdefghijklmnopqrst");
    expect(masked).not.toContain("uvw");
  });

  it("masks credential values with special characters", () => {
    const input = 'token=abc$def!ghi';
    const { masked } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:credential]");
    expect(masked).not.toContain("$def");
    expect(masked).not.toContain("!ghi");
  });

  it("masks uppercase scheme connection strings", () => {
    const input = 'POSTGRES://admin:secret@db.host:5432/app';
    const { masked } = maskSensitive(input);
    expect(masked).toContain("[REDACTED:connection-string]");
    expect(masked).not.toContain("secret");
  });

  it("returns zero redactions for clean text", () => {
    const input = "This is a normal log line with no secrets.";
    const { masked, redactionCount } = maskSensitive(input);
    expect(masked).toBe(input);
    expect(redactionCount).toBe(0);
  });
});

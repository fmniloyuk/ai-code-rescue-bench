export type User = { id: string; name: string };

export interface Database {
  get(id: string): Promise<User>;
  update(id: string, name: string): Promise<User>;
}

export interface Cache {
  get(key: string): Promise<User | undefined>;
  set(key: string, value: User): Promise<void>;
  del(key: string): Promise<void>;
}

export class UserService {
  constructor(private readonly db: Database, private readonly cache: Cache) {}

  private key(id: string): string {
    return `user:${id}`;
  }

  async getUser(id: string): Promise<User> {
    const cached = await this.cache.get(this.key(id));
    if (cached) return cached;
    const user = await this.db.get(id);
    await this.cache.set(this.key(id), user);
    return user;
  }

  async updateUser(id: string, name: string): Promise<User> {
    const updated = await this.db.update(id, name);
    return updated;
  }
}

      // Dist is a vector of objects each of which contain (at least):
      //   * count: an integer, representing the number of votes
      //   * alloc: an integer, the allocation. If set on entry, is used
      //   *        as the initial allocation.
      // N is a magnitude.
      // The function returns the calculated quotient ("cifra repartidora") and
      // fills in the `alloc` fields.
      // The dist array will be reordered in an unpredictable way. If order is
      // important, make a copy.
      // If the pre-existing allocations are greater than equal to N, then
      // the function returns 0. Otherwise, it returns the largest possible
      // quotient.
function largestQuotient(q, N, dist, count, alloc) {
  dist.forEach(a => { if (a[alloc]) N -= a[alloc];
                      else a[alloc] = 0;
                    });
  if (N <= 0) return 0;
  dist.sort((a, b) => b[count] * q(a[alloc]) - a[count] * q(b[alloc]));
  var lead;
  for (var i = 0; i < N; ++i) {
    lead = dist[0];
    ++lead[alloc];
    var j = 1;
    while (j < dist.length && 
           dist[j][count] * q(lead[alloc]) > lead[count] * q(dist[j][alloc])) {
      dist[j - 1] = dist[j];
      ++j;
    }
    dist[j - 1] = lead;
  }
  return lead[count] / lead[alloc];
}
function dhondt(N, dist, count="count", alloc="alloc") {
  return largestQuotient(i=>i+1, N, dist, count, alloc); 
}
function sainteLague(N, dist, count="count", alloc="alloc") {
  return largestQuotient(i=>2*i+1, N, dist, count, alloc);
}
function hare(N, dist, count="count", alloc="alloc") {
  var sum = dist.reduce((p,c) => p + c[count], 0);
  var adivrem = dist.map(a => { let n = a[count] * N;
                                let r = n % sum;
                                return [a, (n - r) / sum, r] });
  var need = N - adivrem.reduce((p,c) => p + c[1], 0);
  adivrem.sort((a, b) => b[2] - a[2]);
  adivrem.forEach((adr, i) => adr[0][alloc] = adr[1] + (i < need));
  return sum / N;
}
// Todo: class Alloc
class Vote {
  constructor(district = null,
              parties = [],
              ebn = [null, null, null],
              votes = []) {
    this.district = district;
    this.electors = ebn[0];
    this.blank = ebn[1];
    this.spoiled = ebn[2];
    this.valid = votes.reduce((a,b)=>a+b, 0);
    this.alloc = parties.map(
         (party, i) => ({ party: party, count: votes[i], alloc: 0}));
  }
  accum(other) {
    this.electors += other.electors;
    this.blank += other.blank;
    this.spoiled += other.spoiled;
    this.valid += other.valid;
    var otheralloc = other.alloc;
    if (this.alloc.length == otheralloc.length && 
        this.alloc.every((a, i)=>a.party === otheralloc[i].party))
      this.alloc.forEach((a, i)=>{ a.count += otheralloc[i].count;
                                   a.alloc += otheralloc[i].alloc;});
    else {
      var pmap = new Map;
      this.alloc.forEach(a => pmap.set(a.party, a));
      otheralloc.forEach(
        o => { if (pmap.has(o.party)) {
                 var a = pmap.get(o.party);
                 a.count += o.count;
                 a.alloc += o.alloc;
               } else {
                 this.alloc.push({party: o.party, count: o.count, alloc: o.alloc});
               }
             });
    }
    return this;
  }
}
